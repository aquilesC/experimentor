import sys
import logging

sys.path.append('/home/aquiles/Documents/Programs/Experimentor')

from experimentor.lib.general_functions import from_yaml_to_dict
from measurement.laser_scan import LaserScan

# create logger
logger = logging.getLogger('experimentor')
logger.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)
logger.info('Starting')
experiment = from_yaml_to_dict('config/measurement_example.yml')
LS = LaserScan(experiment)