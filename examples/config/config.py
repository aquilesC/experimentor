from experimentor.config import Config

# Settings specific to the GUI. These settings can be changed if, for example, the GUI is not responsive enough or if
# there is an overflow of information going to the screen (i.e. updates happening>60Hz).
Config.monitor_read_scan = 10  # How many times do we update the signal during 1 wavelength sweep
Config.laser_update = 3000   # How often (in milliseconds) the laser properties are updated.
