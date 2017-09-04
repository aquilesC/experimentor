""" Config file that will be used to specify constants employed in the code.
    A normal user shouldn't interact with this file unless there is a need for fine-tuning the experiment.
"""
import PyDAQmx as nidaq


# Settings specific to the national instruments card. Not all experiments will need this block.
ni_buffer = 50000  # When acquiring in continuous mode, how big is the buffer.
ni_measure_mode = nidaq.DAQmx_Val_Diff
ni_trigger_edge = nidaq.DAQmx_Val_Rising
ni_read_timeout = 0

# Settings specific to the GUI. These settings can be changed if, for example, the GUI is not responsive enough or if
# there is an overflow of information going to the screen (i.e. updates happening>60Hz).
monitor_read_scan = 10  # How many times do we update the signal during 1 wavelength sweep
laser_update = 3000  # How often (in milliseconds) the laser properties are updated.
