# -*- coding: utf-8 -*-
"""
actuator.py
===========
Actuators are all the devices able to modify the experiment. For example a piezo stage is an actuator.
The properties of the actuators are read-only; in principle one cannot change the port at which a specific sensor is plugged
without re-generating the object.
The actuator has a property called value, that can be accessed directly like so:
    ```python
    prop = {'name': 'Actuator 1'}
    a = Actuator(prop)
    a.value = Q_('1nm')
    print(a.value)
    ```
Bear in mind that setting the value of an actuator triggers a communication with a real device. You have to be careful if
there is something connected to it.

"""
import logging

logger = logging.getLogger(__name__)


class Actuator:
    def __init__(self, properties):
        """Sensor class defined by a given set of properties.
        The only mandatory field of properties is the name.
        """
        if 'name' not in properties:
            logger.error('Initializing sensor without name')
            raise Exception('All sensors need a name')
        self.name = properties['name']
        self._properties = properties
        self._device = None
        self._value = None

        logger.info('Started actuator {}'.format(self.name))

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, driver):
        if self._device is not None:
            logger.error('Trying to override an actuator\'s device.')
            raise Exception('Trying to override an actuator\'s device.')
        else:
            self._device = driver

    @property
    def value(self):
        """ The value of the device."""
        return self._value

    @value.setter
    def value(self, value):
        if self._device is None:
            logger.error("Trying to update a value of {} before connecting it to a device".format(self.name))
            raise Exception("Trying to update a value before initializing the driver")
        try:
            self._device.apply_value(self, value)
        except:
            logger.error("Failed to apply {} to {}".format(value, self.name))
            return False

    @property
    def properties(self):
        return self._properties

    def make_ramp(self, ramp_properties):
        """ Sets the actuator to make a ramp if it is in its capabilities.
        Properties established all the properties that are needed for the ramp.
        """
        self.device.make_ramp(self.properties, ramp_properties)