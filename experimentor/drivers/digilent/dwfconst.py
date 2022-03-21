# ##############################################################################
#  Copyright (c) 2021 Aquiles Carattino, Dispertech B.V.                       #
#  dwfconst.py is part of Experimentor.                                       #
#  This file is released under an MIT license.                                 #
#  See LICENSE.MD for more information.                                        #
#                                                                              #
#                                                                              #
#                                                                              #
#  This file has been adapted from the examples provided by Digilent           #
#                                                                              #
# ##############################################################################
"""
Constants for the Digilent devices. They are specified in dwf.h.

.. note::
    This file is an adaptation of the examples provided by Digilent.

The basic approach is to device the parameters into different groups, such as ``DeviceFilter`` or ``AcquisitionModes``.
Each one of them defines some class attributes with values, such as ``All = c_int(0)``. These classes can be used to
directly assess the values specified by Digilent, and they can also be instantiated. For example::

    >>> df = DeviceFilter(c_int(2))
    >>> print(df)
    DeviceFilter - Discovery
    >>> df == DeviceFilter.Discovery
    True
    >>> df == DeviceFilter.DDiscovery
    False

This makes it clear when printing and enables quick comparisons that are easy to interpret. Ideally, the methods that
return parameters should return instantiated classes. And the methods that use parameters as arguments whould implement
them.
"""

from ctypes import c_int, c_ubyte


class BaseConst:
    """ Base Constant to be used by the other groups of constants. It implements two fundamental approaches: it can be
    directly used by passing the result of a function call in the instantiation. This changes the string representation
    of the returned element to show the actual meaning. It also implements a pattern for checking equality, which
    simplifies checking if the returned value is the expected one.

    """
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __str__(self):
        for k in dir(self):
            if not k.startswith('_'):
                v = getattr(self, k)
                print(k, v, self._value)
                if v.value == self._value.value:
                    return f"{self.__class__.__name__} - {k}"
        return f"{self.__class__} with no value"

    def __eq__(self, other):
        try:
            return other.value == self._value.value
        except:
            return False


# device handle
# HDWF
class DeviceHandle:
    none = c_int(0)


# device enumeration filters
class DeviceFilter(BaseConst):
    All = c_int(0)
    EExplorer = c_int(1)
    Discovery = c_int(2)
    Discovery2 = c_int(3)
    DDiscovery = c_int(4)


# device ID
class DeviceID(BaseConst):
    EExplorer = c_int(1)
    Discovery = c_int(2)
    Discovery2 = c_int(3)
    DDiscovery = c_int(4)


# device version
class DeviceVersion(BaseConst):
    EExplorerC = c_int(2)
    EExplorerE = c_int(4)
    EExplorerF = c_int(5)
    DiscoveryA = c_int(1)
    DiscoveryB = c_int(2)
    DiscoveryC = c_int(3)


# trigger source
class TriggerSource(BaseConst):
    none = c_ubyte(0)
    PC = c_ubyte(1)
    DetectorAnalogIn = c_ubyte(2)
    DetectorDigitalIn = c_ubyte(3)
    AnalogIn = c_ubyte(4)
    DigitalIn = c_ubyte(5)
    DigitalOut = c_ubyte(6)
    AnalogOut1 = c_ubyte(7)
    AnalogOut2 = c_ubyte(8)
    AnalogOut3 = c_ubyte(9)
    AnalogOut4 = c_ubyte(10)
    External1 = c_ubyte(11)
    External2 = c_ubyte(12)
    External3 = c_ubyte(13)
    External4 = c_ubyte(14)
    High = c_ubyte(15)
    Low = c_ubyte(16)


# instrument states
class InstrumentState(BaseConst):
    Ready = c_ubyte(0)
    Config = c_ubyte(4)
    Prefill = c_ubyte(5)
    Armed = c_ubyte(1)
    Wait = c_ubyte(7)
    Triggered = c_ubyte(3)
    Running = c_ubyte(3)
    Done = c_ubyte(2)


# DwfEnumConfigInfo
class EnumConfigInfo(BaseConst):
    DECIAnalogInChannelCount = c_int(1)
    DECIAnalogOutChannelCount = c_int(2)
    DECIAnalogIOChannelCount = c_int(3)
    DECIDigitalInChannelCount = c_int(4)
    DECIDigitalOutChannelCount = c_int(5)
    DECIDigitalIOChannelCount = c_int(6)
    DECIAnalogInBufferSize = c_int(7)
    DECIAnalogOutBufferSize = c_int(8)
    DECIDigitalInBufferSize = c_int(9)
    DECIDigitalOutBufferSize = c_int(10)


# acquisition modes:
class AcquisitionMode(BaseConst):
    acqmodeSingle = c_int(0)
    acqmodeScanShift = c_int(1)
    acqmodeScanScreen = c_int(2)
    acqmodeRecord = c_int(3)
    acqmodeOvers = c_int(4)
    acqmodeSingle1 = c_int(5)


# analog acquisition filter:
class AnalogAcquisitionFilter(BaseConst):
    filterDecimate = c_int(0)
    filterAverage = c_int(1)
    filterMinMax = c_int(2)


# analog in trigger mode:
class AnalogInTriggerMode(BaseConst):
    trigtypeEdge = c_int(0)
    trigtypePulse = c_int(1)
    trigtypeTransition = c_int(2)


# trigger slope:
class TriggerSlope(BaseConst):
    TriggerSlopeRise = c_int(0)
    TriggerSlopeFall = c_int(1)
    TriggerSlopeEither = c_int(2)


# trigger length condition
class TriggerLength(BaseConst):
    triglenLess = c_int(0)
    triglenTimeout = c_int(1)
    triglenMore = c_int(2)


# error codes for the functions:
class ErrorCodes(BaseConst):
    dwfercNoErc = c_int(0)  # No error occurred
    dwfercUnknownError = c_int(1)  # API waiting on pending API timed out
    dwfercApiLockTimeout = c_int(2)  # API waiting on pending API timed out
    dwfercAlreadyOpened = c_int(3)  # Device already opened
    dwfercNotSupported = c_int(4)  # Device not supported
    dwfercInvalidParameter0 = c_int(16)  # Invalid parameter sent in API call
    dwfercInvalidParameter1 = c_int(17)  # Invalid parameter sent in API call
    dwfercInvalidParameter2 = c_int(18)  # Invalid parameter sent in API call
    dwfercInvalidParameter3 = c_int(19)  # Invalid parameter sent in API call
    dwfercInvalidParameter4 = c_int(20)  # Invalid parameter sent in API call


# analog out signal types
class AnalogOutSignalType(BaseConst):
    funcDC = c_ubyte(0)
    funcSine = c_ubyte(1)
    funcSquare = c_ubyte(2)
    funcTriangle = c_ubyte(3)
    funcRampUp = c_ubyte(4)
    funcRampDown = c_ubyte(5)
    funcNoise = c_ubyte(6)
    funcPulse = c_ubyte(7)
    funcTrapezium = c_ubyte(8)
    funcSinePower = c_ubyte(9)
    funcCustom = c_ubyte(30)
    funcPlay = c_ubyte(31)


# analog io channel node types
class AnalogChannelNodeType(BaseConst):
    analogioEnable = c_ubyte(1)
    analogioVoltage = c_ubyte(2)
    analogioCurrent = c_ubyte(3)
    analogioPower = c_ubyte(4)
    analogioTemperature = c_ubyte(5)


class AnalogOutNode(BaseConst):
    AnalogOutNodeCarrier = c_int(0)
    AnalogOutNodeFM = c_int(1)
    AnalogOutNodeAM = c_int(2)


class AnalogOutIdle(BaseConst):
    DwfAnalogOutIdleDisable = c_int(0)
    DwfAnalogOutIdleOffset = c_int(1)
    DwfAnalogOutIdleInitial = c_int(2)


class DigitalClockSource(BaseConst):
    DwfDigitalInClockSourceInternal = c_int(0)
    DwfDigitalInClockSourceExternal = c_int(1)


class DigitalInSampleMode(BaseConst):
    DwfDigitalInSampleModeSimple = c_int(0)
    # alternate samples: noise|sample|noise|sample|...
    # where noise is more than 1 transition between 2 samples
    DwfDigitalInSampleModeNoise = c_int(1)


class DigitalOutOutput(BaseConst):
    DwfDigitalOutOutputPushPull = c_int(0)
    DwfDigitalOutOutputOpenDrain = c_int(1)
    DwfDigitalOutOutputOpenSource = c_int(2)
    DwfDigitalOutOutputThreeState = c_int(3)


class DigitalOutType(BaseConst):
    DwfDigitalOutTypePulse = c_int(0)
    DwfDigitalOutTypeCustom = c_int(1)
    DwfDigitalOutTypeRandom = c_int(2)
    DwfDigitalOutTypeROM = c_int(3)
    DwfDigitalOutTypeState = c_int(4)
    DwfDigitalOutTypePlay = c_int(5)


class DigitalOutIdle(BaseConst):
    DwfDigitalOutIdleInit = c_int(0)
    DwfDigitalOutIdleLow = c_int(1)
    DwfDigitalOutIdleHigh = c_int(2)
    DwfDigitalOutIdleZet = c_int(3)


class AnalogImpedance(BaseConst):
    DwfAnalogImpedanceImpedance = c_int(0)
    DwfAnalogImpedanceImpedancePhase = c_int(1)
    DwfAnalogImpedanceResistance = c_int(2)
    DwfAnalogImpedanceReactance = c_int(3)
    DwfAnalogImpedanceAdmittance = c_int(4)
    DwfAnalogImpedanceAdmittancePhase = c_int(5)
    DwfAnalogImpedanceConductance = c_int(6)
    DwfAnalogImpedanceSusceptance = c_int(7)
    DwfAnalogImpedanceSeriesCapactance = c_int(8)
    DwfAnalogImpedanceParallelCapacitance = c_int(9)
    DwfAnalogImpedanceSeriesInductance = c_int(10)
    DwfAnalogImpedanceParallelInductance = c_int(11)
    DwfAnalogImpedanceDissipation = c_int(12)
    DwfAnalogImpedanceQuality = c_int(13)


class Params(BaseConst):
    DwfParamUsbPower = c_int(2)  # 1 keep the USB power enabled even when AUX is connected, Analog Discovery 2
    DwfParamLedBrightness = c_int(3)  # LED brightness 0 ... 100%, Digital Discovery
    DwfParamOnClose = c_int(4)  # 0 continue, 1 stop, 2 shutdown
    DwfParamAudioOut = c_int(5)  # 0 disable / 1 enable audio output, Analog Discovery 1, 2
    DwfParamUsbLimit = c_int(6)  # 0..1000 mA USB power limit, -1 no limit, Analog Discovery 1, 2


# TRIGCOND
class TriggerCondition(BaseConst):
    trigcondRisingPositive = c_int(0)
    trigcondFallingNegative = c_int(1)
