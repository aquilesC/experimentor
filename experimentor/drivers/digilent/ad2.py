# ##############################################################################
#  Copyright (c) 2021 Aquiles Carattino, Dispertech B.V.                       #
#  ad2.py is part of Experimentor.                                             #
#  This file is released under an MIT license.                                 #
#  See LICENSE.MD for more information.                                        #
# ##############################################################################

"""
Drivers for the Analog Discovery 2 board (they may also work with other boards). The idea is to wrap the methods
that appear in the examples to make them more "Pythonic". At the time of writing (July 2021), Digilent has provided
only with a low-level c-API library that is filled with values passed by reference and other patterns that are not
common for a Python developer.

This driver is not aimed at being exhaustive but rather focused on the objectives at hand, namely using the analog
acquisition synchronized via an external trigger (which can also be on the board itself).
"""
import sys
from ctypes import byref, c_bool, c_double, c_int, cdll, create_string_buffer

from experimentor.drivers.exceptions import DriverException
from experimentor.lib.log import get_logger

logger = get_logger()

try:
    if sys.platform.startswith("win"):
        dwf = cdll.dwf
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")
except:
    logger.error("The library for controlling the digilent cards was not found. Please check your own "
                 "installation before proceeding")
    raise


class AnalogDiscovery:
    def __init__(self):
        self.hdwf = c_int()

    def initialize(self, dev_num=-1):
        """ Initialize the communication with a device identified by its order

        Parameters
        ----------
        dev_num : int
            The device number to open, by default it opens the last device

        Raises
        ------
        DriverException
            If the device can't be opened
        """

        dwf.FDwfDeviceOpen(c_int(dev_num), byref(self.hdwf))

        if self.hdwf.value == 0:
            szerr = create_string_buffer(512)
            dwf.FDwfGetLastErrorMsg(szerr)
            raise DriverException(str(szerr.value))

    def analog_out_count(self):
        """The number of analog output channels available on this board.

        Returns
        -------
        int
            The number of analog channels available
        """
        num_channels = c_int()
        dwf.FDwfAnalogOutCount(self.hdwf, byref(num_channels))
        return num_channels.value

    def analog_in_frequency_set(self, frequency):
        dwf.FDwfAnalogInFrequencySet(self.hdwf, c_double(frequency))

    def analog_buffer_in_size_set(self, buffer_size):
        dwf.FDwfAnalogInBufferSizeSet(self.hdwf, c_int(buffer_size))

    def analog_in_channel_enable(self, channel):
        dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(channel), c_bool(True))

    def analog_in_channel_disable(self, channel):
        dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(channel), c_bool(False))

    def analog_in_channel_range_set(self, channel, range):
        dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(channel), c_double(range))

    def analog_in_trigger_auto_timeout(self, timeout=0):
        dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, c_double(timeout))

    def analog_in_trigger_source_set(self, source):
        dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, source)

    def analog_in_trigger_type_set(self, trig_type):
        dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, trig_type)

    def analog_in_trigger_channel_set(self, channel):
        dwf.FDwfAnalogInTriggerChannelSet(self.hdwf, c_int(channel))

    def analog_in_trigger_level(self, level):
        dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, c_double(level))

    def analog_in_trigger_condition(self, condition):
        dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, condition)