"""
    Place to store general functions that may be used throwout the program.
"""
import sys
import yaml
from .device import Device
from .logger_with_time import logger

def from_yaml_to_devices(filename = "config/devices.yml", name=None):
    """ Reads a YAML file and returns a list of devices.
    :param filename: File where the data is stored
    :param name: The name of the device to load
    :return: list of :class: device
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


if __name__ == "__main__":
    d = from_yaml_to_devices('../../config/devices.yml',name='Santec Laser')
    print(d)