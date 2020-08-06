# -*- coding: utf-8 -*-
"""
    Sensor
    ======
    Sensors are all the devices able to get a value from the experiment. For example a thermocouple is a sensor.
    The properties of the sensor are read-only; in principle one cannot change the port at which a specific sensor is plugged
    without re-generating the object.

    .. sectionauthor:: Aquiles Carattino
"""
import logging

logger = logging.getLogger(__name__)


class Sensor:
    def __init__(self, properties):
        """Sensor class defined by a given set of properties.
        The only mandatory field is the name.
        """
        if 'name' not in properties:
            logger.error('Initializing sensor without name')
            raise Exception('All sensors need a name')

        self.name = properties['name']
        self._value = None
        self._properties = properties

    def add_device(self, device):
        """ Adds the driver to the current sensor. In this context a driver is a class able to read the value from the
        device.
        """
        self.device = device

    @property
    def value(self):
        if self.device is None:
            err_str = "Trying to read from {} but there is no device associated.".format(self.name)
            logger.error(err_str)
            raise Exception(err_str)

        return self.device.read_value(self)

    @property
    def properties(self):
        return self._properties

    def __str__(self):
        return self.name