# -*- coding: utf-8 -*-
"""
    pharos.controller.santec.tsl710
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Driver for the tsl710 laser, based on the manual provided, following the Command set List 2 page 7-38).
    It is not compliant with IEEE-488.2, but is available also to RS-232 and USB.
"""

from lantz import Feat, Action
from lantz.messagebased import MessageBasedDriver
from pyvisa import constants


class tsl710(MessageBasedDriver):
    DEFAULTS = {'COMMON': {'encoding': 'ascii',
                            'read_termination': '\r\n',
                            'write_termination': '\r\n',
                         },
                'ASRL': {'baud_rate': 1200,
                         'bytesize': 8,
                         'parity': constants.Parity.none,
                         'stop_bits': constants.StopBits.one,}}

    def initialize(self):
        super().initialize()
        self.coherent = False
        self.LD = False
        self.trigger_status = False
        self.auto_power_status = False
        self.shutter_status = False

    @Feat()
    def idn(self):
        return self.query('*IDN?')

    @Feat(units='nm', limits=(1480, 1640, 0.0001))
    def wavelength(self):
        return self.query('WA')

    @wavelength.setter
    def wavelength(self, value):
        self.query('WA%.4f' % value)

    @Feat(units='THz')
    def frequency(self):
        return self.query('FQ')

    @frequency.setter
    def frequency(self, value):
        self.query('FQ%.5f' % value)

    @Feat(limits=(-100, 100, 0.01))
    def fine_tune(self):
        return self.query('FT')

    @fine_tune.setter
    def fine_tune(self, value):
        self.query('FT%.2f' % value)

    @Action()
    def fine_tune_stop(self):
        """
        Stops fine-tuning mode and starts closed-loop wavelength controlling.
        :return:
        """
        self.query('FTF')

    @Feat(limits=(-20, 10, 0.01))
    def powerdB(self):
        """
        Sets the optical power in dBm
        :return:
        """
        return self.query('OP')

    @powerdB.setter
    def powerdB(self, value):
        self.query('OP%.2f' % value)

    @Feat(units='mW', limits=(0.01, 10, 0.01))
    def powermW(self):
        """
        sets the optical power in mW
        :return:
        """
        return self.query('LP')

    @powermW.setter
    def powermW(self, value):
        self.query('LP%.2f' % value)


    @Action()
    def auto_power_on(self):
        """Sets the power control to auto."""
        self.query('AF')

    @Action()
    def manual_power(self):
        self.query('AO')

    @Feat(units='dB', limits=(0, 30, 0.01))
    def attenuator(self):
        return self.query('AT')

    @attenuator.setter
    def attenuator(self, value):
        self.query('AT%.2f' % value)


    @Feat(units='nm', limits=(1480, 1640, 0.0001))
    def stop_wavelength(self):
        """Stop sweep wavelength."""
        return self.query('SE')

    @stop_wavelength.setter
    def stop_wavelength(self, value):
        self.query('SE%.4f' % value)
        
    @Feat(units='nm', limits=(1480, 1640, 0.0001))
    def start_wavelength(self):
        return self.query('SS')

    @start_wavelength.setter
    def start_wavelength(self, value):
        self.query('SS%.4f'%value)
        
    @Feat(units='THz')
    def start_frequency(self):
        """Start sweep frequency."""
        return self.query('SS')
    
    @start_frequency.setter
    def start_frequency(self, value):
        self.query('SS%.5f' % value)

    @Feat(units='THz')
    def stop_frequency(self):
        """Sweep stop frequency."""
        return self.query('FF')

    @stop_frequency.setter
    def stop_frequency(self, value):
        self.query('FF%.5f' % value)

    @Feat(units='s', limits=(0, 999.9, 0.1))
    def wait_time(self):
        """Wait time between each sweep in continuous sweep operation."""
        return self.query('SA')

    @wait_time.setter
    def wait_time(self, value):
        self.query('SA%.1f' % value)

    @Feat(units='s', limits=(0, 999.9, 0.1))
    def step_time(self):
        """Amount of time spent during each step in step sweep operation."""
        return self.query('SB')

    @step_time.setter
    def step_time(self, value):
        self.query('SB%.1f' % value)

    @Feat(limits=(0, 999, 1))
    def wavelength_sweeps(self):
        """Number of wavelengths sweeps."""
        return self.query('SZ')

    @wavelength_sweeps.setter
    def wavelength_sweeps(self, value):
        self.query('SZ%i' % value)

    @Feat(limits=(0.5, 100, 0.1))
    def wavelength_speed(self):
        """Speed for continuous sweeps (in nm/s)"""
        return self.query('SN')

    @wavelength_speed.setter
    def wavelength_speed(self, value):
        self.query('SN%.1f' % value)

    @Feat(units='nm', limits=(0.0001, 160, 0.0001))
    def step_wavelength(self):
        """Step interval (wavelength) of step sweeps. """
        return self.query('WW')

    @step_wavelength.setter
    def step_wavelength(self, value):
        self.query('WW%.4f' % value)

    @Feat(units='THz', limits=(0.00002, 19.76219, 0.00001))
    def step_frequency(self):
        return self.query('WF')

    @step_frequency.setter
    def step_frequency(self, value):
        self.query('WF%.5f' % value)

    @Feat(values={
        'ContOne': 1,
        'ContTwo': 2,
        'StepOne': 3,
        'StepTwo': 4,
        'StepOneFreq': 5,
        'StepTwoFreq': 6,
        'ContOneTrig': 7,
        'ContTwoTrig': 8,
        'StepOneTrig': 9,
        'StepTwoTrig': 10,
        'StepOneFreqTrig': 11,
        'StepTwoFreqTrig': 12
    })
    def sweep_mode(self):
        return self.query('SM')

    @sweep_mode.setter
    def sweep_mode(self, value):
        self.query('SM%s' % value)

    @Action()
    def execute_sweep(self):
        """
        Executes sweeps or puts the device in trigger signal standby.
        The number of sweeps is defined by the method wavelength_sweeps.
        """
        self.query('SG')

    @Action()
    def pause_sweep(self):
        self.query('SP')

    @Action()
    def stop_sweep(self):
        self.query('SQ')

    @Action()
    def resume_sweep(self):
        self.query('SR')

    @Action()
    def software_trigger(self):
        self.query('ST')

    @Feat()
    def number_sweeps(self):
        return self.query('SX')

    @Feat(values={
        'Stop': 0,
        'Executing': 1,
        'Pause': 2,
        'Awaiting trigger': 3,
        'Setting to sweep start wavelength': 4
    })
    def sweep_condition(self):
        return int(self.query('SK'))


    @Feat(values={
        'None': 0,
        'Stop': 1,
        'Start': 2,
        'Step': 3
    })
    def timing_trigger(self):
        return self.query('TM')

    @timing_trigger.setter
    def timing_trigger(self, value):
        self.query('TM%i' % value)

    @Feat(units='nm', limits=(0.0001, 160, 0.0001))
    def interval_trigger(self):
        """Sets the interval of the trigger signal output."""
        return self.query('TW')

    @interval_trigger.setter
    def interval_trigger(self, value):
        self.query('TW%.4f' % value)

    @Feat(values={True: True, False: False})
    def coherent_control(self):
       return self.coherent

    @coherent_control.setter
    def coherent_control(self, value):
       if value:
           self.coherent_control_on()
           print('Coherent ON')
       else:
           self.coherent_control_off
           print('Coherent off')
       self.coherent = value

    @Feat(values={True: True, False: False})
    def LD_current(self):
       return self.LD

    @LD_current.setter
    def LD_current(self, value):
       if value:
           self.lo()
       else:
           self.lf()
       self.LD = value

    @Feat(values={True: True, False: False})
    def auto_power(self):
        return self.auto_power_status

    @auto_power.setter
    def auto_power(self, value):
        if value:
            self.auto_power_on()
        else:
            self.manual_power()
        self.auto_power_status = value

    @Feat(values={True: True, False: False})
    def trigger(self):
        return self.trigger_status

    @trigger.setter
    def trigger(self, value):
        if value:
            self.enable_trigger()
        else:
            self.disable_trigger()
        self.trigger_status = value

    @Feat(values={True: True, False: False})
    def shutter(self):
        return self.shutter_status

    @shutter.setter
    def shutter(self, value):
        if value:
            self.open_shutter()
        else:
            self.close_shutter()
        self.shutter_status = value

    @Action()
    def close_shutter(self):
        self.query('SC')

    @Action()
    def open_shutter(self):
        self.query('SO')

    @Action()
    def enable_trigger(self):
        self.query('TRE')

    @Action()
    def disable_trigger(self):
        self.query('TRD')

    @Action()
    def lo(self):
        """
        Sets ON the LD current
        :return:
        """
        self.query('LO')

    @Action()
    def lf(self):
        """
        Sets OFF the LD current.
        :return:
        """
        self.query('LF')

    @Action()
    def coherent_control_on(self):
        self.query('CO')

    @Action()
    def coherent_control_off(self):
        self.query('CF')
if __name__ == '__main__':
    from lantz.ui.app import start_test_app

    with tsl710.via_gpib(1) as inst:
        start_test_app(inst)

#if __name__ == '__main__':
#    from lantz import Q_
#    nm = Q_('nm')
#    with tsl710.via_gpib(1) as inst:
#        print('Instrument identified as %s' % inst.idn)
#        print('Current wavelength: %s' % inst.wavelength)
#        print('Changing wavelength to 1492nm')
#        inst.wavelength = 1492*nm
#        print(inst.query('SS'))
#        print('Current wavelength: %s' % inst.wavelength)
#        inst.start_wavelength = 1501*nm
#        inst.stop_wavelength = 1520*nm
#        print('Stop wavelength: %s' % inst.stop_wavelength)
#        print('Start wavelength: %s' % inst.start_wavelength)
#        