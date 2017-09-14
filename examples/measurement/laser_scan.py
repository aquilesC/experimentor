# -*- coding: utf-8 -*-
"""
    laser_scan
    ==========
    Class for controlling the Pharos setup. Everything revolves around triggering the scan of a laser and acquiring
    signals of different devices via an NI-DAQ card.
    Ultimately it should also be able to change values of serial devices.

"""
import numpy as np
import logging

from time import sleep
from experimentor.experiment.base_experiment import Experiment

from experimentor import Q_
from experimentor.lib.general_functions import from_yaml_to_dict
from experimentor.config import Config

logger = logging.getLogger(__name__)


class LaserScan(Experiment):
    def __init__(self, measure):
        """Measurement class that will hold all the information regarding the experiment being performed.
        :param measure: a dictionary with the necessary steps
        """
        super().__init__(measure)
        self.logger = logging.getLogger(__name__)
        logger.info('Init Laser Scan')
        devices = from_yaml_to_dict(self.init['devices'])
        actuators = from_yaml_to_dict(self.init['actuators'])
        sensors = from_yaml_to_dict(self.init['sensors'])
        self.load_devices(devices)
        self.load_sensors(sensors)
        self.load_actuators(actuators)
        self.initialize_devices()

    def setup_scan(self):
        """ Prepares the scan by setting all the parameters to the DAQs and laser.

        .. warning:: ALL THIS IS WORK IN PROGRESS, THAT WORKS WITH VERY SPECIFIC SETUP CONDITIONS!
        """

        # First setup the laser
        laser_params = self.scan['laser']['params']
        laser = self.devices[self.scan['laser']['name']]['dev']

        # When setting up 2D scans, only 1 sweep is supported
        if 'wavelength_sweeps' in laser_params:
            if laser_params['wavelength_sweeps'] != 1:
                logger.warning('2D scans only support 1 sweep.')

        laser_params['wavelength_sweeps'] = 1

        laser.apply_values(laser_params)
        num_points = int(
            (laser.params['stop_wavelength'] - laser.params['start_wavelength']) / laser.params['interval_trigger'])

        # Estimated accuracy to set the DAQmx to.
        accuracy = laser.params['interval_trigger'] / laser.params['wavelength_speed']

        # Conditions to be passed to the DAQ.
        conditions = {
            'accuracy': accuracy,
            'points': num_points
        }

        # Then setup the ADQs
        for device in self.scan['detectors']:
            dev = self.devices[device]['dev']
            sensors = []
            if dev.properties['model'] == 'ni':
                self.logger.debug('NI card devices')
                sens_to_monitor = self.scan['detectors']
                for sensor in sens_to_monitor:
                    self.logger.debug('Setting up {} for scans'.format(sensor))
                    if sensor not in self.devices[device]['sensor']:
                        self.logger.warning('Trying to read {} from {}, but was not registered'.format(sensor, device))
                        raise Warning('Sensor not found')
                    else:
                        s = self.devices['sensors'][sensor]
                        sensors.append(s)
                self.logger.info('Going to monitor {} devices.'.format(len(sensors)))
                daq_driver = dev.driver
                conditions.update({
                    'sensors': sensors,
                    'trigger': dev.properties['trigger'],
                    'trigger_source': dev.properties['trigger_souruce'],
                })
                self.scan_task = daq_driver.analog_input_setup(conditions)

    def do_scan(self):
        """ Does the scan considering that everything else was already set up.
        """

        scan = self.scan
        laser = self.devices[scan['laser']['name']]
        axis = scan['axis']
        approx_time_to_scan = (laser.params['stop_wavelength']-laser.params['start_wavelength'])/laser.params['wavelength_speed']
        self.logger.info('Total number of devices to scan: {}'.format(len(axis)))
        self.logger.info('Approximate time to do a laser scan: {}'.format(approx_time_to_scan))

        if len(axis) != 1:
            self.logger.warning('Trying to do a scan of {} dimensions. The program only supports 1 dimenstion'.format(len(axis)))
            raise Warning('Wrong number of axis')

        dev_to_scan = list(axis.keys())[-1] # Get the name of the device
        actuator_to_scan = list(axis[dev_to_scan].keys())[-1]
        range = axis[dev_to_scan][actuator_to_scan]['rage']
        # Scan the laser and the values of the given device
        if dev_to_scan != 'time':
            start = Q_(range[0])
            stop = Q_(range[1])
            step = Q_(range[2])
            units = start.u
            num_points_dev = ((stop-start)/step).to('') + 1 # This is to include also the last point
        else:
            start = 1
            stop = range[1]
            num_points_dev = stop

        for value in np.linspace(start, stop, num_points_dev):
            if dev_to_scan != 'time':
                self.devices[dev_to_scan]['actuators'][actuator_to_scan].value = value * units
                self.logger.debug('Set {} to {}'.format(actuator_to_scan, value))

            for d in self.scans['detectors']:
                dev = self.devices[d]['dev']
                if dev.properties['model'] != 'ni':
                    self.logger.warning('Trying to read from a non NI device.')
                    raise Warning('Reading from other than NI is not yet implemented.')
                self.logger.info('Starting task in {}'.format(d))
                daq_driver = dev.driver
                if daq_driver.driver.is_task_complete():
                    daq_driver.driver.trigger_analog()

            laser.driver.execute_sweep()
            self.logger.info('Executing laser sweep')
            sleep(0.1)
            while laser.driver.sweep_condition != 'Stop':
                sleep(approx_time_to_scan.m/Config.Laser.number_checks_per_scan)

    def set_value_to_device(self, dev_name, value):
        """ Sets the value of the device. If it is an analog output, it takes just one value.
        If it is a device connected through serial, etc. it takes a dictionary.
        :param dev_name: name of the device to set the output
        :param value: value or dict of values to set the device to
        """
        dev = self.devices[dev_name]
        # If it is an analog channel
        if dev.properties['connection']['type'] == 'daq':
            daq = self.devices[dev.properties['connection']['device']]
            conditions = {
                'dev': dev,
                'value': value
            }
            daq.driver.analog_output_dc(conditions)
        else:
            self.devices[dev.dev.properties['name']].apply_values(value)

    def setup_continuous_scans(self, monitor=None):
        """ Sets up 1D scans. This is useful for monitoring a signal over time.
        """
        self.logger.info('Setting up continuous scans')

        if monitor is None:
            monitor = self.monitor
        else:
            self.monitor = monitor

        # Lets grab the laser
        laser = self.devices[monitor['laser']['name']]
        laser.apply_values(monitor['laser']['params'])

        # Lets see what happens with the devices to monitor
        devices_to_monitor = monitor['detectors']

        # Lets calculate the conditions of the scan
        num_points = int(
            (laser.params['stop_wavelength'] - laser.params['start_wavelength']) / laser.params['trigger_step'])
        accuracy = laser.params['trigger_step'] / laser.params['wavelength_speed']

        self.logger.debug('1D scan with {} number of points'.format(num_points))

        approx_time_to_scan = (laser.params['stop_wavelength'] - laser.params['start_wavelength']) / laser.params[
            'wavelength_speed']
        self.logger.debug('Approx time to scan: {}'.format(approx_time_to_scan))

        self.measure['monitor']['approx_time_to_scan'] = approx_time_to_scan

        conditions = {
            'accuracy': accuracy,
            'points': num_points
        }

        # Then setup the ADQs
        for device in devices_to_monitor:
            dev = self.devices[device]['dev']  # Get the DAQ.
            sensors = []
            for sensor in d:
                if sensor not in daq:
                    self.logger.warning('Trying ro read sensor {} not associated with the proper DAQ {}.'.format(sensor, daq))
                    raise Warning('Sensor not associated with this device.')

            daq_driver = self.devices[d]  # Gets the link to the DAQ
            if len(daq['monitor']) > 0:
                print('DAQ: %s' % d)
                devs_to_monitor = daq['monitor']  # daqs dictionary groups the channels by daq to which they are plugged
                print('Devs to monitor:')
                print(devs_to_monitor)
                conditions['devices'] = devs_to_monitor
                conditions['trigger'] = daq_driver.properties['trigger']
                print('Trigger: %s' % conditions['trigger'])
                conditions['trigger_source'] = daq_driver.properties['trigger_source']
                print('Trigger source: %s' % conditions['trigger_source'])
                conditions['sampling'] = 'continuous'
                daq['monitor_task'] = daq_driver.driver.analog_input_setup(conditions)
                self.daqs[d] = daq  # Store it back to the class variable
                print('Task number: %s' % self.daqs[d]['monitor_task'])

    def start_continuous_scans(self):
        """Starts the laser, and triggers the daqs. It assumes setup_continuous_scans was already called."""
        monitor = self.monitor
        laser = self.devices[monitor['laser']['name']]

        for d in self.daqs:
            daq = self.daqs[d]
            daq_driver = self.devices[d].driver
            if len(daq['monitor'])>0:
                devs_to_monitor = daq['monitor']  # daqs dictionary groups the channels by daq to which they are plugged             
                if daq_driver.is_task_complete(daq['monitor_task']):
                    daq_driver.trigger_analog(daq['monitor_task'])

        laser.driver.execute_sweep()

    def read_continuous_scans(self, devs):
        """ Reads the values being acquired while the scan is running.
        It is thought for monitoring signals in real time.

        :param devs: Devices to read from
        :type devs: list
        """
        conditions = {'points': -1}  # To read all the points available
        data = {}
        for d in devs:
            daq = self.daqs[d]
            daq_driver = self.devices[d]
            if len(daq['monitor']) > 0:
                vv, dd = daq_driver.driver.read_analog(daq['monitor_task'], conditions)
                dd = dd[:vv*len(daq['monitor'])]
                dd = np.reshape(dd, (len(daq['monitor']), int(vv)))
                for i in range(len(daq['monitor'])):
                    dev = daq['monitor'][i]
                    data[dev.properties['name']] = dd[i,:]
        return data
    
    def stop_continuous_scans(self):
        monitor = self.monitor
        laser = self.devices[monitor['laser']['name']].driver
        laser.pause_sweep()
        laser.stop_sweep()
        for d in self.daqs:
            daq = self.daqs[d]
            if len(daq['monitor']) > 0:
                daq_driver = self.devices[d].driver
                daq_driver.stop_task(daq['monitor_task'])
                daq_driver.clear_task(daq['monitor_task'])

    def pause_continuous_scans(self):
        monitor = self.monitor
        laser = self.devices[monitor['laser']['name']].driver
        laser.pause_sweep()

    def resume_continuous_scans(self):
        monitor = self.monitor
        laser = self.devices[monitor['laser']['name']].driver
        laser.execute_sweep()


if __name__ == "__main__":
    import logging

    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.FileHandler('example.log')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug('This message should go to the log file')
    logger.info('So should this')
    logger.warning('And this, too')

    import os
    BASE_DIR = '/home/aquiles/Documents/Programs/Experimentor/examples/'
    # config_experiment = "config/measurement_example.yml"
    # experiment_dict = from_yaml_to_dict(os.path.join(BASE_DIR, config_experiment))
    experiment_dict = ''
    experiment = LaserScan(experiment_dict)
    devices_file = "config/devices.yml"
    experiment.load_devices(from_yaml_to_dict(os.path.join(BASE_DIR,devices_file)))
    experiment.setup_scan()