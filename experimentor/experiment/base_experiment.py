"""
    base_experiment
    ===============
    Base class for the experiment. It provides the basic functions that are common to other experiments.

    .. sectionauthor:: Aquiles Carattino <aquiles@uetke.com>
"""
from ..lib.device import Device
from ..lib.actuator import Actuator
from ..lib.sensor import Sensor
from ..lib.general_functions import from_yaml_to_dict


class Experiment(object):
    def __init__(self, measure):
        self.devices = {}
        self.actuators = {}
        self.sensors = {}
        self.loaded_devices = False
        self.loaded_sensors = False
        self.loaded_actuators = False

        self.dict_measure = measure  # Dictionary of the measurement steps
        # This short block is going to become useful in the future, when interfacing with a GUI
        for d in measure:
            setattr(self, d, measure[d])
            
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
                self.devices[dev] = {'dev': Device(devices_dict[dev]),
                                     'actuators': {},
                                     'sensors': {}}
                print('Added {} to the experiment'.format(dev))
        self.loaded_devices = True
        return True

    def load_actuators(self, actuators_dict, source=None):
        """
        Loads the actuators from a dictionary to the class.
        :param actuators_dict: Dictionary of actuators, the first key is the device that owns them.
        :param source: Not yet implemented.
        """
        if source is not None:
            return False

        if not self.loaded_devices:
            raise Exception('The devices have to be loaded before loading the actuators.')

        for dev in actuators_dict:
            if dev not in self.devices:
                raise Exception('The device specified in the Actuator file does not exist in the device file')
            # Get all the actuators connected to the device
            acts = actuators_dict[dev]
            for act in acts:
                act_data = acts[act]
                if act in self.devices[dev]['actuators']:
                    raise Exception('Actuator possibly double defined. Check that there are no two actuators with \
                                    the same main key connected to the same device.')
                self.devices[dev]['actuators'][act] = Actuator(act_data)
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

        if not self.loaded_devices:
            raise Exception('The devices have to be loaded before loading the sensors')

        for dev in sensors_dict:
            if dev not in self.devices:
                raise Exception('The device specified in the Sensor file does not exist in the device file.')
            # get all the sensors connected to the device
            sens = sensors_dict[dev]
            for sen in sens:
                sen_data = sens[sen]
                if sen in self.devices[dev]['sensors']:
                    raise Exception('Sensor possibly double defifned. Check that there are no two actuators with \
                                    the same main key connected to the same device.')
                self.devices[dev]['sensors'][sen] = Sensor(sen_data)
        self.loaded_sensors = True
        return True

    def initialize_devices(self):
        """ Initializes the devices. It means that it will load the appropriate drivers and check if there are defaults
        defined and will apply them.
        """
        if not self.loaded_devices:
            raise Exception('Devices have to be loaded before being initialized.')

        for dev in self.devices:
            d = self.devices[dev] # This is the Device class
            d.initialize_driver()
            if 'defaults' in dev.properties:
                defaults_file = dev.properties['defaults']
                defaults = from_yaml_to_dict(defaults_file)[dev.properties['name']]
                dev.apply_values(defaults)



    def initalize(self):
        pass

    def finalize(self):
        pass
