"""
sensor.py
=========
Sensors are all devices that are able to get a value from the experiment. For example a thermocouple is a sensor.

"""


class sensor:
    def __init__(self, properties):
        """Sensor class defined by a given set of properties.
        The only mandatory field is the name.
        """
        self.name = properties['name']
        self.properties = properties

    def add_driver(self, driver):
        """ Adds the driver to the current sensor. In this context a driver is a class able to read the value from the
        device.
        """
        self.driver = driver

    def get_value(self):
        self.driver.read(self.properties)

    def __str__(self):
        return self.name