"""
device.py
=========
Devices are connected to the computer. They control sensors and actuators. A device has to be able to set and read
values.
Setting complex devices such as a laser would require to define it as a device and its properties as sensors or
actuators respectively.

"""
import importlib
from lantz import Q_



class device(object):
    def __init__(self, properties):
        self.properties = properties
        self.driver = None
        self.params = {}

    def add_driver(self, driver):
        """ Adds the driver of the device. It has to be initialized()
        :param driver: driver of any class.
        :return: Null
        """
        self.driver = driver

    def initialize_driver(self):
        if 'driver' in self.properties:
            d = self.properties['driver'].split('/')
            driver_class = getattr(importlib.import_module(d[0]), d[1])
            if 'connection' in self.properties:
                connection_type = self.properties['connection']['type']
                if connection_type == 'GPIB':
                    # Assume it is a lantz driver
                    self.driver = driver_class.via_gpib(self.properties['connection']['port'])
                    self.driver.initialize()
                elif connection_type == 'USB':
                    # Assume it is a lantz driver
                    self.driver = driver_class.via_usb()
                    self.driver.initialize()
                    raise Warning('This was never tested!')
                elif connection_type == 'serial':
                    # Assume it is a lantz driver
                    self.driver = driver_class.via_serial(self.properties['connection']['port'])
                    self.driver.initialize()
                    raise Warning('This was never tested!')
                elif connection_type == 'daq':
                    self.driver = driver_class(self.properties['connection']['port'])


    def apply_values(self, values):
        """ Iterates over all values of a dictionary and sets the values of the driver to it.
        :param values: a dictionary of parameters and desired values for those parameters
        :return:
        """
        if isinstance(values, dict):
            for k in values:
                try:
                    # Tries to convert to proper units, if it fails it uses the value as is
                    value = Q_(values[k])
                except:
                    value = values[k]
                print('Setting %s to %s'%(k, value))
                try:
                    setattr(self.driver, k, values[k])
                except:
                    print('Problem setting %s in %s' % (k, self))
                self.params[k] = value
        else:
            raise Exception('Drivers can only update dictionaries')

    def get_params(self):
        return self.params

    def __str__(self):
        if 'name' in self.properties:
            return self.properties['name']
        else:
            return "Device with no name"

if __name__ == "__main__":
    from pharos.model.lib.general_functions import from_yaml_to_devices

    d = from_yaml_to_devices('../../config/devices.yml', name='dummy daq')[0]
    d.initialize_driver()
    print(d)