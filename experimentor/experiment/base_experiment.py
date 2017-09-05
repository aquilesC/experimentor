"""
    base_experiment
    ===============
    Base class for the experiment. It provides the basic functions that are common to other experiments.

    .. sectionauthor:: Aquiles Carattino <aquiles@uetke.com>
"""
from ..lib.device import Device
from ..lib.actuator import Actuator
from ..lib.sensor import Sensor


class Experiment(object):
    def __init__(self):
        self.devices = {}
        self.actuators = {}
        self.sensors = {}
        self.loaded_devices = False
        self.loaded_sensors = False
        self.loaded_actuators = False

    def load_devices(self, devices_dict, source=None):
        """ Loads the devices from a dictionary.
        :param devices_dict: Dictionary of devices.
        :param source: Not implemented yet.
        """
        if source is not None:
            return False

        for dev in devices_dict:
            # Check that the name of the device is not in the dictionary of devices
            if not dev in self.devices:
                self.devices[dev] = Device(devices_dict[dev])
                print('Added %s to the experiment'.format(dev))
        self.loaded_devices = True
        return True

    def load_actuators(self, actuators_dict, source=None):
        """
        Loads the actuators from a dictionary to the class.
        :param actuators_dict: Dictionary of actuators
        :param source: Not yet implemented.
        """
        if source is not None:
            return False

        for act in actuators_dict:
            # Check that the actuator is not already defined
            if not act in self.actuators:
                self.actuators[act] = Actuator(actuators_dict[act])
        self.loaded_actuators = True
        return True

    def load_sensors(self, sensors_dict, source=None):
        """
        Loads the sensors from a dictionary to the class,
        :param sensors_dict: Dictionary of sensors
        :param source: Not yet implemented
        """
        if source is not None:
            return False

        for sens in sensors_dict:
            # Check that the sensor does not exist in the class yet
            if not sens in self.sensors:
                self.sensors[sens] = Sensor(sensors_dict[sens])
        self.loaded_sensors = True
        return True

    def get_sensors_from_device(self, device):
        """ Returns a list of of names of the sensors connected to a specific device.
        :param device: name of the device to look for
        :return: List of names
        :vartype device: str
        """
        sensors = []
        for sens in self.sensors:
            if self.sensors[sens].connection['device'] == device:
                sensors.append(sens)
        return sensors

    def get_actuators_from_device(self, device):
        """ Returns a list of names of the sensors connected to a specific device.
        :param device: name of the device to look for.
        :return: List of names
         :vartype device: str"""
        actuators = []
        for act in self.actuators:
            if self.actuators[act].connection['device'] == device:
                actuators.append(act)
        return actuators




    def initalize(self):
        pass

    def finalize(self):
        pass
