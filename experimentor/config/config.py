# -*- coding: utf-8 -*-
"""
Configuration
==============

Config file that will be used to specify constants employed in the code.
A normal user shouldn't interact with this file unless there is an extreme need to change the default behaviour.

For overwriting or adding new values to the config, the following should be done

.. code-block:: python

    from experimentor.config import Config
    Config.new_property = 'new_value'
    Config.old_property = 'override value'

In this way, whenever the config is used in the Experimentor package, the new values will be available.
Remember that you are modifying the class properties, not an instance of the Config class, and that is why it is
inherited by the rest of the code.

.. warning:: If you need to change the values of the config, you should do it before the importing of the rest of
    the Experimentor happens.

"""
from warnings import warn

try:
    import PyDAQmx as nidaq
except ModuleNotFoundError:
    nidaq = None
    warn('Check whether you need to install PyDAQmx')


zmq_publisher_port = 5556
zmq_listener_port = 5557
exit = "exit"

class Config(object):
    # Settings specific to the national instruments card. Not all experiments will need this block.
    ni_buffer = 50000  # When acquiring in continuous mode, how big is the buffer.
    if nidaq:
        ni_measure_mode = nidaq.DAQmx_Val_Diff
        ni_trigger_edge = nidaq.DAQmx_Val_Rising
    ni_read_timeout = 0

    class Laser:
        number_checks_per_scan = 10  # How many times it checks if the 1D scan is done.

    class NI:
        """ Default values for the National Instruments ADQ cards."""
        class Output:
            """ Output values """
            class Analog:
                """ Analog channels """
                timeout = 0  # It does not timeout.
        class Input:
            """ Input values """
            class Analog:
                """ Analog channels """
                freq = 1/1000  # kHz, in order to do an average of 10 measurements in 10ms.
                num_points = 10
                trigger = ""  # Internal trigger
                if nidaq:
                    trigger_edge = nidaq.DAQmx_Val_Rising
                    measure_mode = nidaq.DAQmx_Val_Diff
                    cont_finite = nidaq.DAQmx_Val_FiniteSamps
                read_timeout = 0
