"""
    laser_scan
    ==========
    Class for controlling the Pharos setup. Everything revolves around triggering the scan of a laser and acquiring
    signals of different devices via an NI-DAQ card.
    Ultimately it should also be able to change values of serial devices.

"""
import numpy as np
from time import sleep
from experimentor.experiment.base_experiment import Experiment

from experimentor import Q_
from experimentor.lib.general_functions import from_yaml_to_dict


class LaserScan(Experiment):
    def __init__(self, measure):
        """Measurement class that will hold all the information regarding the experiment being performed.
        :param measure: a dictionary with the necessary steps
        """
        super(LaserScan, self).__init__()

        self.dict_measure = measure  # Dictionary of the measurement steps
        # This short block is going to become useful in the future, when interfacing with a GUI
        for d in measure:
            setattr(self, d, measure[d])


    def setup_scan(self):
        """ Prepares the scan by setting all the parameters to the DAQs and laser.
        ALL THIS IS WORK IN PROGRESS, THAT WORKS WITH VERY SPECIFIC SETUP CONDITIONS!
        :return:
        """

        # First setup the laser
        laser_params = self.scan['laser']['params']
        laser = self.devices[self.scan['laser']['name']]['dev']
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
            daq = self.devices[device]['dev']
            sens_to_monitor = self.scan['detectors'][device]
            for sensor in sens_to_monitor:
                if sensor not in daq
            # TODO: Finish this!!

        # for d in self.daqs:
        #     daq = self.daqs[d]  # Get the DAQ from the dictionary of daqs.
        #     daq_driver = self.devices[d]  # Gets the link to the DAQ
        #     if len(daq['monitor']) > 0:
        #         print('DAQ: %s' % d)
        #         devs_to_monitor = daq['monitor']  # daqs dictionary groups the channels by daq to which they are plugged
        #         print('Devs to monitor:')
        #         print(devs_to_monitor)
        #         conditions['devices'] = devs_to_monitor
        #         conditions['trigger'] = daq_driver.properties['trigger']
        #         conditions['trigger_source'] = daq_driver.properties['trigger_source']
        #         daq['monitor_task'] = daq_driver.driver.analog_input_setup(conditions)
        #         self.daqs[d] = daq # Store it back to the class variable

    def do_scan(self):
        """ Does the scan considering that everything else was already set up.
        """
        scan = self.measure['scan']
        laser = self.devices[scan['laser']['name']]
        axis = scan['axis']
        approx_time_to_scan = (laser.params['stop_wavelength']-laser.params['start_wavelength'])/laser.params['wavelength_speed']
        print('Total number of devices to scan: %s' % len(axis))
        print('Approximate time to do a laser scan: %s' % approx_time_to_scan)
        data_scan = {} # To store all the data
        for dev_to_scan in axis:
            # Set all the devices to their default value
            for dev_name in axis:
                if dev_name != 'time':
                    value = Q_(axis[dev_name]['default'])
                    self.set_value_to_device(dev_name, value)

            # Scan the laser and the values of the given device
            if dev_to_scan != 'time':
                dev_range = axis[dev_to_scan]['range']
                start = Q_(dev_range[0])
                stop = Q_(dev_range[1])
                step = Q_(dev_range[2])
                units = start.u
                num_points_dev = ((stop-start)/step).to('')
            else:
                start = 1
                stop = axis['time']['repetitions']
                num_points_dev = stop

            data_scan[dev_to_scan] = []
            for value in np.linspace(start, stop, num_points_dev):
                if dev_to_scan != 'time':
                    self.set_value_to_device(dev_to_scan, value * units)
                for d in self.daqs:
                    daq = self.daqs[d]  # Get the DAQ from the dictionary of daqs.
                    daq_driver = self.devices[d]  # Gets the link to the DAQ
                    if len(daq['monitor']) > 0:
                        if daq_driver.driver.is_task_complete(daq['monitor_task']):
                            daq_driver.driver.trigger_analog(daq['monitor_task'])
                laser.driver.execute_sweep()
                sleep(0.1)
                while laser.driver.sweep_condition != 'Stop':
                    sleep(approx_time_to_scan.m/10) # It checks 10 times, maybe overkill?
                conditions = {
                    'points': 0,
                }
                for d in self.daqs:
                    daq = self.daqs[d]  # Get the DAQ from the dictionary of daqs.
                    if len(daq['monitor']) > 0:
                        v, dd = self.devices[d].driver.read_analog(daq['monitor_task'], conditions)
                        sleep(1)
                        #self.devices[d].driver.stop_task(daq['monitor_task'])
                        data_scan[dev_to_scan].append(dd)
                        print('Acquired data!')
                        print('Total data points: %s' % len(data_scan[dev_to_scan][-1]))
        return data_scan

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
        """ Sets up scans that continuously start. This is useful for monitoring a signal over time.
        In principle it is similar to
        :return:
        """
        if monitor is None:
            monitor = self.monitor
        else:
            self.monitor = monitor

        # Lets grab the laser
        laser = self.devices[monitor['laser']['name']]
        monitor['laser']['params']['wavelength_sweeps'] = 0  # This will generate the laser to sweep always.
                                                             # CAUTION!: It will have to be stopped when the program finished.
        laser.apply_values(monitor['laser']['params'])

        # Clear the array to start afresh
        for d in self.daqs:
            self.daqs[d]['monitor'] = []

        # Lets see what happens with the devices to monitor
        devices_to_monitor = monitor['detectors']

        for dev in devices_to_monitor:
            #dev = self.devices[d]
            self.daqs[dev.properties['connection']['device']]['monitor'].append(dev)

        # Lets calculate the conditions of the scan
        print(laser.params)
        num_points = int(
            (laser.params['stop_wavelength'] - laser.params['start_wavelength']) / laser.params['trigger_step'])
        accuracy = laser.params['trigger_step'] / laser.params['wavelength_speed']

        approx_time_to_scan = (laser.params['stop_wavelength'] - laser.params['start_wavelength']) / laser.params[
            'wavelength_speed']

        self.measure['monitor']['approx_time_to_scan'] = approx_time_to_scan

        conditions = {
            'accuracy': accuracy,
            'points': num_points
        }

        # Then setup the ADQs
        for d in self.daqs:
            daq = self.daqs[d]  # Get the DAQ from the dictionary of daqs.
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

    def read_continuous_scans(self):
        conditions = {'points': -1} # To read all the points available
        data = {}
        for d in self.daqs:
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
    import os
    BASE_DIR = '/home/aquiles/Documents/Programs/Experimentor/examples/'
    config_experiment = "config/measurement_example.yml"
    experiment_dict = from_yaml_to_dict(os.path.join(BASE_DIR, config_experiment))
    experiment = LaserScan(experiment_dict)
    devices_file = "config/devices.yml"
    experiment.load_devices(from_yaml_to_dict(os.path.join(BASE_DIR,devices_file)))
    experiment.setup_scan()