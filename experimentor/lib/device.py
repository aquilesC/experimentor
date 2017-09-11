# -*- coding: utf-8 -*-
"""
device.py
=========
Devices are connected to the computer. They control sensors and actuators. A device has to be able to set and read
values.
Setting complex devices such as a laser would require to define it as a device and its properties as sensors or
actuators respectively.

.. warning::

    If problems arise when adding new devices, tt is important to check :meth:initialize_driver .
    It was hardcoded which parameters are passed when initializing each device type.

.. todo::

    Make flexible parameters when initializing the driver of the devices.
"""
import logging
import importlib
from .. import Q_

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, properties):
        if 'name' in properties:
            logger.debug('Loaded properties of {}'.format(properties['name']))
            self._name = properties['name']
        else:
            logger.debug('Loaded properties of device without name')
            self._name = 'nameless'

        self.properties = properties
        self.driver = None
        self._params = {}

    def add_driver(self, driver):
        """ Adds the driver of the device. It has to be initialized()
        :param driver: driver of any class.
        :return: Null
        """
        self.driver = driver
        logger.debug('Added driver to {}'.format(self._name))

    def initialize_driver(self):
        """ Initializes the driver.
        There are 4 types of possible connections:

        - GPIB
        - USB
        - serial
        - daq

        The first 3 are based on Lantz and its initialization routine, while daq was inherited from previous code and
        has a different initialization routine."""

        if 'driver' in self.properties:
            d = self.properties['driver'].split('/')
            driver_class = getattr(importlib.import_module(d[0]), d[1])
            if 'connection' in self.properties:
                connection_type = self.properties['connection']['type']
                logger.debug('Initializing {} connection'.format(connection_type))
                try:
                    if connection_type == 'GPIB':
                        # Assume it is a lantz driver
                        self.driver = driver_class.via_gpib(self.properties['connection']['port'])
                        self.driver.initialize()
                    elif connection_type == 'USB':
                        # Assume it is a lantz driver
                        self.driver = driver_class.via_usb()
                        self.driver.initialize()
                        logger.warning('Connection {} was never tested.'.format(connection_type))
                        raise Warning('This was never tested!')
                    elif connection_type == 'serial':
                        # Assume it is a lantz driver
                        self.driver = driver_class.via_serial(self.properties['connection']['port'])
                        self.driver.initialize()
                        logger.warning('Connection {} was never tested.'.format(connection_type))
                        raise Warning('This was never tested!')
                    elif connection_type == 'daq':
                        self.driver = driver_class(self.properties['connection']['port'])
                except:
                    logger.error('{} driver for {} not initialized'.format(connection_type, self._name))
                    raise Exception('Driver not initialized')

    def apply_values(self, values):
        """ Iterates over all values of a dictionary and sets the values of the driver to it.
        :param values: a dictionary of parameters and desired values for those parameters. The parameters should have units.
        """
        if self.driver is None:
            logger.error('Trying to apply values before initializing the driver')
            raise Exception('Driver not yet initialized')

        if isinstance(values, dict):
            for k in values:
                if not isinstance(values[k], Q_):
                    try:
                        # Tries to convert to proper units, if it fails it uses the value as is
                        value = Q_(values[k])
                    except:
                        logger.warning('Value {} could not be converted to Quantity'.format(values[k]))
                        value = values[k]

                logger.info('Setting {} to {:~}'.format(k, value))
                try:
                    setattr(self.driver, k, values[k])
                except:
                    logger.error('Problem setting %s in %s' % (k, self))
                self._params[k] = value
        else:
            logger.error('Drivers can only update dictionaries')
            raise Exception('Drivers can only update dictionaries')

    @property
    def params(self):
        return self._params

    def __str__(self):
        return self._name