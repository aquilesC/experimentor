# -*- coding: utf-8 -*-
"""
    ni6251.py
    ---------
    Class for comunicating with the NI-6251 DAQ. It requires to have installed the DAQmx (provided by NI) and the
    pyDAQmx package (from pypy). It does not check for dependencies automatically, so it is up to the user to have them.
    This model is far from complete; the place to start is the
    `DAQmx C Reference <http://zone.ni.com/reference/en-XX/help/370471AA-01/>`_

     .. sectionauthor:: Aquiles Carattino <aquiles@uetke.com>
"""
import logging
import time

import PyDAQmx as nidaq
import numpy as np

from experimentor import Q_
from ._skeleton import Daq
from ...config import Config
from ...lib.general_functions import from_units_to_volts, from_volts_to_units
logger = logging.getLogger(__name__)


class NI(Daq):
    model = "6251"
    def __init__(self, daq_num=1):
        """Class trap for condensing tasks that can be used for interacting with an optical trap.
        session -- class with important variables, including the adq card.
        """
        super().__init__()
        self.daq_num = daq_num
        self.monitorNum = []
        self.tasks = []
        self.nidaq = nidaq
        logger.info('Started NI instrument with number: {}'.format(daq_num))

    def apply_value(self, actuator, value):
        """ Sets the output of the NI card. For the time being it sets a DC constant value; this has to be expanded to
        other types of actuators, for example a digital output.

        .. todo:: Make this method work with actuators of different types than analog

        .. warning:: This method is not intended for making ramps or generating a continuous output; it is just a handy
        way of changing the value of a particular port.

        :param actuator: specifies the actuator on which to act.
        :param value: The value to be set
        """


        port = actuator.properties['port']

        # First let's check that the actuator is an analog channel
        if actuator.properties['type'] == 'analog':
            port = "Dev%s/ao%s" % (self.daq_num, port)
            calibration = actuator.calibration
            # Convert value to volts:
            output_volts = from_units_to_volts(value, calibration)

            min_value = Q_(actuator.properties['limits']['min'])
            max_value = Q_(actuator.properties['limits']['max'])
            # Convert values to volts:
            # The NI card needs to specify min and max voltages; the actuator itself should check that the voltages
            # are within limits before even arriving here. In any case, as a safe, the NI card will never output a value
            # beyond the limits.

            min_V = from_units_to_volts(min_value, calibration)
            max_V = from_units_to_volts(max_value, calibration)

            autostart = nidaq.bool32(True)
            timeout = Config.NI.Output.Analog.timeout
            logger.debug('Actuator: {}, MIN: {}, MAX: {}, Value: {}'.format(actuator.name, min_V, max_V, output_volts))
            t = nidaq.Task()
            t.CreateAOVoltageChan(port, None, min_V, max_V, nidaq.DAQmx_Val_Volts, None)
            t.WriteAnalogScalarF64(autostart, timeout, output_volts, None)
            t.StopTask()
            t.ClearTask()

        logger.info('Changed the value of {} to {}'.format(actuator.name, value))

    def read_value(self, sensor):
        """ Reads the value of a sensor.

        .. todo:: Make this method work with sensors other than analog inputs.

        :param sensor: the sensor to read.
        :return: The value read, with units if appropriate.
        """
        port = sensor.properties['port']

        if sensor.properties['type'] == 'analog':
            port = "Dev%s/ai%s" % (self.daq_num, port)
            calibration = sensor.properties['calibration']
            min_value = Q_(sensor.properties['limits']['min'])
            max_value = Q_(sensor.properties['limits']['max'])
            min_V = from_units_to_volts(min_value, calibration)
            max_V = from_units_to_volts(max_value, calibration)

            freq = Config.NI.Input.Analog.freq
            trigger = Config.NI.Input.Analog.trigger
            trigger_edge = Config.NI.Input.Analog.trigger_edge
            measure_mode = Config.NI.Input.Analog.measure_mode
            num_points = Config.NI.Input.Analog.num_points
            cont_finite = Config.NI.Input.Analog.cont_finite

            t = nidaq.Task()
            t.CreateAIVoltageChan(port, None, measure_mode, min_V,
                                  max_V, nidaq.DAQmx_Val_Volts, None)
            t.CfgSampClkTiming(trigger, freq, trigger_edge, cont_finite, num_points)
            t.StartTask()
            time.sleep(num_points*freq)
            timeout = Config.NI.Input.Analog.read_timeout
            read = nidaq.int32()
            data = np.zeros((num_points,), dtype=np.float64)

            t.ReadAnalogF64(num_points, timeout, nidaq.DAQmx_Val_GroupByChannel,
                            data, num_points, nidaq.byref(read), None)

            value = np.mean(data)
            return from_volts_to_units(value, calibration)

    def analog_input_setup(self, conditions):
        """
        Sets up a task for acquaring a number of analog channels.
        conditions -- dictionary with the needed conditions to set up an acquisition.

        """
        t = nidaq.Task()
        dev = 'Dev%s' % self.daq_num
        devices = conditions['devices']
        if not isinstance(devices, list):
            channel = ["Dev%s/ai%s" % (self.daq_num, devices.properties['port'])]
            limit_min = [devices.properties['limits']['min']]
            limit_max = [devices.properties['limits']['max']]
        else:
            channel = []
            limit_max = []
            limit_min = []
            for dev in conditions['devices']:
                channel.append("Dev%s/ai%s" % (self.daq_num, dev.properties['port']))
                limit_min.append(dev.properties['limits']['min'])
                limit_max.append(dev.properties['limits']['max'])

        channels = ', '.join(channel)
        channels.encode('utf-8')
        freq = int(1 / conditions['accuracy'].to('s').magnitude)
        # freq = freq.magnitude
        logger.debug('SAMPLES PER SECOND: %s' % freq)
        if conditions['trigger'] == 'external':
            trigger = "/Dev%s/%s" % (self.daq_num, conditions['trigger_source'])
            logger.debug('NI: external trigger: %s' % trigger)
        else:
            trigger = ""
        if 'trigger_edge' in conditions:
            if conditions['trigger_edge'] == 'rising':
                trigger_edge = nidaq.DAQmx_Val_Rising
            elif conditions['trigger_edge'] == 'falling':
                trigger_edge = nidaq.DAQmx_Val_Falling
        else:
            trigger_edge = Config.ni_trigger_edge

        if 'measure_mode' in conditions:
            measure_mode = conditions['measure_mode']
        else:
            measure_mode = Config.ni_measure_mode

        t.CreateAIVoltageChan(channels, None, measure_mode, min(limit_min),
                              max(limit_max), nidaq.DAQmx_Val_Volts, None)

        if conditions['points'] > 0:
            if 'sampling' in conditions:
                if conditions['sampling'] == 'finite':
                    cont_finite = nidaq.DAQmx_Val_FiniteSamps
                elif conditions['sampling'] == 'continuous':
                    cont_finite = nidaq.DAQmx_Val_ContSamps
                else:
                    raise Exception('Sampling mode not understood')
            else:
                cont_finite = nidaq.DAQmx_Val_FiniteSamps
            num_points = conditions['points']
        else:
            cont_finite = nidaq.DAQmx_Val_ContSamps
            num_points = Config.ni_buffer

        t.CfgSampClkTiming(trigger, freq, trigger_edge, cont_finite, num_points)
        self.tasks.append(t)
        return len(self.tasks) - 1

    def trigger_analog(self, task=None):
        """
        :param task: Task number to be triggered.
        :return:
        """
        if task is None:
            t = self.tasks[-1]
        else:
            t = self.tasks[task]
        t.StartTask()  # Starts the measurement.

    def read_analog(self, task, conditions):
        """Gets the analog values acquired with the triggerAnalog function.
        conditions -- dictionary with the number of points ot be read
        """
        if task is None:
            t = self.tasks[-1]
        else:
            t = self.tasks[task]

        read = nidaq.int32()
        points = int(conditions['points'])
        if points > 0:
            data = np.zeros((points,), dtype=np.float64)
            t.ReadAnalogF64(points, Config.ni_read_timeout, nidaq.DAQmx_Val_GroupByChannel,
                            data, points, nidaq.byref(read), None)
        else:
            data = np.zeros((Config.ni_buffer,), dtype=np.float64)
            t.ReadAnalogF64(points, Config.ni_read_timeout, nidaq.DAQmx_Val_GroupByChannel,
                            data, len(data), nidaq.byref(read), None)
        values = read.value
        return values, data

    def from_volt_to_units(self, value, dev):
        pass

    def from_units_to_volts(self, value, dev):
        """ Converts a value from specific actuator units into volts to pass to a DAQ.

        :param value: The output value
        :param dev: The calibration of the device, including units.
        :type value: Quantity
        :type dev: dict.
        """
        units = Q_(dev.properties['calibration']['units'])
        slope = dev.properties['calibration']['slope'] * units
        offset = dev.properties['calibration']['offset'] * units
        value = value.to(units)
        value = value.m
        slope = slope.m
        offset = offset.m
        return (value - offset) / slope

    def analog_output_dc(self, conditions):
        """ Sets the analog output of the NI card. For the time being is thought as a DC constant value.

        :param dict conditions: specifies DEV and Value
        :return:
        """
        dev = conditions['dev']
        port = "Dev%s/ao%s" % (self.daq_num, dev.properties['port'])
        units = Q_(dev.properties['calibration']['units'])
        min_value = Q_(dev.properties['limits']['min']).to(units)
        max_value = Q_(dev.properties['limits']['max']).to(units)
        # Convert values to volts:
        value = conditions['value'].to(units)
        V = self.from_units_to_volts(value, dev)
        min_V = self.from_units_to_volts(min_value, dev)
        max_V = self.from_units_to_volts(max_value, dev)
        t = nidaq.Task()
        t.CreateAOVoltageChan(port, None, min_V, max_V, nidaq.DAQmx_Val_Volts, None)
        t.WriteAnalogScalarF64(nidaq.bool32(True), 0, V, None)
        t.StopTask()
        t.ClearTask()

    def analog_output_samples(self, conditions):
        """ Prepares an anlog output from an array of values.
        :param conditions: dictionary of conditions.
        :return:
        """
        t = nidaq.Task()
        dev = conditions['dev'][0]
        port = dev.properties['port']

        min_val = self.from_units_to_volts(dev.properties['limits']['min'], dev)
        max_val = self.from_units_to_volts(dev.properties['limits']['max'], dev)

        t.CreateAOVoltageChan('Dev%s/ao%s' % (self.daq_num, port), None, min_val, max_val, nidaq.DAQmx_Val_Volts,
                              None, )

        freq = int(1 / conditions['accuracy'].to('s').magnitude)
        num_points = len(conditions['data'])

        t.CfgSampClkTiming('', freq, Config.ni_trigger_edge, nidaq.DAQmx_Val_FiniteSamps, num_points)

        auto_trigger = nidaq.bool32(0)
        timeout = -1
        dataLayout = nidaq.DAQmx_Val_GroupByChannel
        read = nidaq.int32()

        t.WriteAnalogF64(num_points, auto_trigger, timeout, dataLayout, conditions['data'], read, None)

        self.tasks.append(t)
        return len(self.tasks) - 1

    def is_task_complete(self, task):
        t = self.tasks[task]
        d = nidaq.bool32()
        t.GetTaskComplete(d)
        return d.value

    def stop_task(self, task):
        t = self.tasks[task]
        t.StopTask()

    def clear_task(self, task):
        t = self.tasks[task]
        t.ClearTask()

    def reset_device(self):
        nidaq.DAQmxResetDevice('Dev%s' % self.daq_num)


if __name__ == '__main__':
    print(Config.monitor_read_scan)
    # a = NI(3)
    # b = 10 * Q_('ms')
    # print(type(b))
    # # b = Q_(b, 'seconds')
    # print(1 / b.to('seconds'))
    # print(nidaq.DAQmx_Val_Falling)
    # print(b.magnitude)
