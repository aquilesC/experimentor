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
from ctypes import byref, c_bool, c_byte, c_double, c_int, cdll, create_string_buffer

import numpy as np

from experimentor.drivers.digilent.dwfconst import InstrumentState
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

    def analog_in_reset(self):
        dwf.FDwfAnalogInReset(self.hdwf)

    def analog_in_configure(self, reconfigure=1, start=1):
        dwf.FDwfAnalogInConfigure(self.hdwf, c_int(reconfigure), c_int(start))

    def analog_in_status(self, read_data=0):
        """ Checks the status of the acquisition

        Parameters
        ----------
        read_data : int
            0 or 1, to indicate whether data should be read from the device

        Returns
        -------
        InstrumentState
            The instrument state
        """
        state = c_byte()
        dwf.FDwfAnalogInStatus(self.hdwf, c_int(read_data), byref(state))
        return InstrumentState(state)

    def analog_in_samples_left(self):
        """
            Retrieves the number of samples left in the acquisition.
        Returns
        -------
        int
            Number of samples remaining
        """
        samples = c_int()
        dwf.FDwfAnalogInStatusSamplesLeft(self.hdwf, byref(samples))
        return samples.value

    def analog_in_samples_valid(self):
        samples = c_int()
        dwf.FDwfAnalogInStatusSamplesValid(self.hdwf, byref(samples))
        return samples.value

    def analog_in_status_index(self):
        """
        Retrieves the buffer write pointer which is needed in ScanScreen acquisition mode to display the scan bar.
        Returns
        -------
        int
            Variable to receive the position of the acquisition.
        """
        index = c_int()
        dwf.FDwfAnalogInStatusIndexWrite(self.hdwf, byref(index))
        return index.value

    def analog_in_status_auto_trigger(self):
        """
            Verifies if the acquisition is auto triggered.
        Returns
        -------
        int :
            I guess it returns 1 if the acquisition was auto triggered
        """
        auto = c_int()
        dwf.FDwfAnalogInStatusAutoTriggered(self.hdwf, byref(auto))
        return auto.value

    def analog_in_status_data(self, channel, samples, buffer=None):
        """ Retrieves the acquired data samples from the specified idxChannel on the AnalogIn instrument. It copies the
            data samples to the provided buffer.

        Parameters
        ----------
        channel : int
        samples : int
        buffer : c_double array, optional

        Returns
        -------
        np.array :
            Array with the data
        """
        if buffer is None:
            buffer = (c_double * samples)()
        dwf.FDwfAnalogInStatusData(self.hdwf, c_int(channel), byref(buffer), samples)
        return np.array(buffer)

    def analog_in_status_data_2(self, channel, first, samples, buffer=None):
        """
            Retrieves the acquired data samples from the specified idxChannel on the AnalogIn instrument. It copies the
            data samples to the provided buffer or creates a new buffer. This method allows to specify which data will
            be copied. To retrieve all data see :meth:`~analog_in_status_data`.

        Parameters
        ----------
        channel : int
        first : int
        samples : int
        buffer : c_double array, optional

        Returns
        -------
        numpy.array :
            Array with the data
        """
        if buffer is None:
            buffer = (c_double * samples)()
        dwf.FDwfAnalogInStatusData2(self.hdwf, c_int(channel), byref(buffer), c_int(first), c_int(samples))
        return np.array(buffer)

    def analog_in_status_data_16(self, channel, first, samples, buffer=None):
        """
        Retrieves the acquired raw data samples from the specified idxChannel on the AnalogIn instrument. It copies the
        data samples to the provided buffer or creates a new one. This is the **raw** data, as opposed to what
        :meth:`~analog_in_status_data` returns.

        Parameters
        ----------
        channel : int
        first : int
        samples : int
        buffer : c_double array, optional

        Returns
        -------
        numpy.array :
            Array with the data
        """
        if buffer is None:
            buffer = (c_double * samples)()
        dwf.FDwfAnalogInStatusData16(self.hdwf, c_int(channel), byref(buffer), c_int(first), c_int(samples))
        return np.array(buffer)

    def analog_in_status_noise(self, channel, samples):
        """ Retrieves the acquired noise samples from the specified idxChannel on the AnalogIn instrument.

        Parameters
        ----------
        channel : int
        samples : int

        Returns
        -------
        2-colum numpy.array :
            minimum noise data, maximum noise data
        """
        min_buffer = (c_double * samples)()
        max_buffer = (c_double * samples)()
        dwf.FDwfAnalogInStatusNoise(self.hdwf, c_int(channel), byref(min_buffer), byref(max_buffer), c_int(samples))
        min_buffer = np.array(min_buffer)
        max_buffer = np.array(max_buffer)
        return np.stack((min_buffer, max_buffer))

    def analog_in_status_sample(self, channel):
        """ Gets the last ADC conversion sample from the specified idxChannel on the AnalogIn instrument.

        Parameters
        ----------
        channel : int

        Returns
        -------
        float :
            Sample value
        """
        value = c_double()
        dwf.FDwfAnalogInStatusSample(self.hdwf, c_int(channel), byref(value))
        return value.value

    def analog_in_status_record(self):
        """ Retrieves information about the recording process. The data loss occurs when the device acquisition is
        faster than the read process to PC. In this case, the device recording buffer is filled and data samples are
        overwritten. Corrupt samples indicate that the samples have been overwritten by the acquisition process during
        the previous read. In this case, try optimizing the loop process for faster execution or reduce the acquisition
        frequency or record length to be less than or equal to the device buffer size
        (record length <= buffer size/frequency).


        Returns
        -------
        data_available : int
            Available number of samples
        data_lost : int
            Lost samples after the last check
        data_corrupt : int
            Number of samples that can be corrupt
        """
        data_available = c_int()
        data_lost = c_int()
        data_corrupt = c_int()

        dwf.FDwfAnalogInStatusRecord(self.hdwf, byref(data_available), byref(data_lost), byref(data_corrupt))
        return data_available.value, data_lost.value, data_corrupt.value

    def analog_in_record_length_set(self, length):
        dwf.FDwfAnalogInRecordLengthGet(self.hdwf, c_double(length))

    def analog_in_record_length_get(self):
        length = c_double()
        dwf.FDwfAnalogInRecordLengthSet(self.hdwf, byref(length))
        return length.value

    def analog_in_frequency_info(self):
        """ Retrieves the minimum and maximum (ADC frequency) settable sample frequency.

        Returns
        -------
        min_freq : float
            Minimum allowed frequency
        max_freq : float
            Maximum allowed frequency
        """
        min_freq = c_double()
        max_freq = c_double()
        dwf.FDwfAnalogInFrequencyInfo(self.hdwf, byref(min_freq), byref(max_freq))
        return min_freq.value, max_freq.value

    def analog_in_frequency_set(self, frequency):
        dwf.FDwfAnalogInFrequencySet(self.hdwf, c_double(frequency))

    def analog_in_frequency_get(self):
        frequency = c_double()
        dwf.FDwfAnalogInFrequencyGet(self.hdwf, byref(frequency))
        return frequency.value

    def analog_in_bits_info(self):
        bits = c_int()
        dwf.FDwfAnalogInBitsInfo(self.hdwf, byref(bits))
        return bits.value

    def analog_in_buffer_size_info(self):
        min_buff = c_int()
        max_buff = c_int()
        dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, byref(min_buff), byref(max_buff))
        return min_buff.value, max_buff.value

    def analog_in_buffer_size_set(self, buffer_size):
        dwf.FDwfAnalogInBufferSizeSet(self.hdwf, c_int(buffer_size))

    def analog_in_buffer_size_get(self):
        buffer_size = c_int()
        dwf.FDwfAnalogInBufferSizeGet(self.hdwf, byref(buffer_size))
        return buffer_size.value

    def analog_in_noise_size_info(self):
        buffer_size = c_int()
        dwf.FDwfAnalogInNoiseSizeInfo(self.hdwf, byref(buffer_size))
        return buffer_size.value

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

    def analog_in_trigger_level_set(self, level):
        dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, c_double(level))

    def analog_in_trigger_level_get(self):
        level = c_double()
        dwf.FDwfAnalogInTriggerLevelGet(self.hdwf, byref(level))
        return level.value

    def analog_in_trigger_condition(self, condition):
        dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, condition)
