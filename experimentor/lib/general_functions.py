# -*- coding: utf-8 -*-
"""
    general_functions
    =================
    Place to store general functions that may be used throughout the program.
    They normally refer to functions for interacting with files, the stdout, etc.
    Some are not used but can be handy for future developers.

    .. sectionauthor:: Aquiles Carattino <aquiles@uetke.com>

"""
import sys
import yaml
from .device import Device
from .logger_with_time import logger
from .. import Q_

def from_yaml_to_devices(filename = "config/devices.yml", name=None):
    """ Reads a YAML file and returns a list of devices.

    :param filename: File where the data is stored
    :param name: The name of the device to load
    :return: list of devices
    :type return: Device
    """
    with open(filename, 'r') as stream:
        devices = yaml.load(stream)
    devs = {}
    if name is not None:
        if name in devices:
            devs[name] = Device(devices[name])
            return devs
        else:
            return None
    else:
        for d in devices:
            dev = devices[d]
            dd = Device(dev)
            devs[d] = dd
    return devs


def from_yaml_to_dict(filename='config/measurement.yml'):
    with open(filename, 'r') as stream:
        output = yaml.load(stream)
    return output


def start_logger(filename=None):
    sys.stdout = logger(filename)


def stop_logger():
    sys.stdout = sys.stdout.old_stdout

def from_volts_to_units(self, value, calibration):
    """ Converts a value from volts (given by an ADQ for example) to specific sensor units.
    The quation is: [Units] = value*slope+offset

    :param value: The value read by the ADQ
    :param calibration: The calibration of the sensor, including units.
    :return: The calibrated value of the detector, with appropriate units.
    :type value: Quantity
    :type calibration: dict.
    """
    units = Q_(calibration['units'])
    slope = calibration['slope'] * units
    offset = calibration['offset'] * units
    value = value.to('V')
    value = value.m
    slope = slope
    offset = offset
    return value*slope+offset


def from_units_to_volts(self, value, calibration):
    """ Converts a value from specific actuator units into volts to pass to a DAQ.
    The quation is: [Volts] = (value - offset) / slope

    :param value: The output value with units
    :param calibration: The calibration of the actuator, including units.
    :type value: Quantity
    :type calibration: dict.
    """
    units = Q_(calibration['units'])
    slope = calibration['slope'] * units
    offset = calibration['offset'] * units
    value = value.to(units)
    value = value.m
    slope = slope.m
    offset = offset.m
    return (value - offset) / slope


if __name__ == "__main__":
    d = from_yaml_to_devices('../../config/devices.yml',name='Santec Laser')
    print(d)