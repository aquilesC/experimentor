"""
    Place to store general functions that may be used throwout the program.
"""
import sys
import yaml
from pharos.model.lib.device import device
from .logger_with_time import logger

def from_yaml_to_devices(filename = "config/devices.yml", name=None):
    """ Reads a YAML file and returns a list of devices.
    :param filename: File where the data is stored
    :param name: The name of the device to load
    :return: list of :class: device
    """

    stream = open(filename, 'r')
    devices = yaml.load(stream)
    stream.close()
    devs = []
    for d in devices:
        dev = devices[d]
        if name is not None:
            try:
                if dev['name'] == name:
                    dd = device(dev)
                    devs.append(dd)
            except:
                pass
        else:
            dd = device(dev)
            devs.append(dd)
    return devs


def from_yaml_to_dict(filename='config/measurement.yml'):
    stream = open(filename, 'r')
    output = yaml.load(stream)
    stream.close()
    return output


def start_logger(filename=None):
    sys.stdout = logger(filename)


def stop_logger():
    sys.stdout = sys.stdout.old_stdout


if __name__ == "__main__":
    d = from_yaml_to_devices('../../config/devices.yml',name='Santec Laser')
    print(d)