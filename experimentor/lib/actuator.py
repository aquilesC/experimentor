"""
actuator.py
===========
Actuators are all the devices able to modify the experiment. For example a piezo stage is an actuator.
"""


class Actuator:
    def __init__(self, properties):
        """Sensor class defined by a given set of properties.
        The only mandatory field is the name.
        """
        self.name = properties['name']
        self.properties = properties

    def add_driver(self, driver):
        self.device = driver

    def set_value(self, value):
        try:
            return value
        except:
            return False

    def make_ramp(self, ramp_properties):
        """ Sets the actuator to make a ramp if it is in its capabilities.
        Properties established all the properties that are needed for the ramp.
        """
        self.device.make_ramp(self.properties, ramp_properties)