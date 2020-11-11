"""
    Global Settings
    ---------------

    Settings that should be available to any experimentor project. If you are starting a new project, you can use the
    settings below as an example, and override the ones you think need to be overwritten. Especially things like:

      - EXPERIMENT_MODEL
      - EXPERIMENT_MODEL_INIT
      - START_WINDOW

    The only variables that will be considered are those written all in CAPITAL LETTERS.
"""

from multiprocessing import Event

EXPERIMENT_MODEL = 'experimentor.models.experiments.Experiment'
EXPERIMENT_MODEL_INIT = None
# EXPERIMENT_MODEL_INIT = {
#     'config_file': 'config.yml',
# }

START_WINDOW = 'experimentor.views.DataViewWidget'

PUBLISHER_EXIT_KEYWORD = 'stop'
SUBSCRIBER_EXIT_KEYWORD = 'stop'

GENERAL_STOP_EVENT = Event()

PUBLISHER_READY = True
