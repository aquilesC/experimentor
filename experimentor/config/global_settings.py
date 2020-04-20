from multiprocessing import Event

PUBLISHER_PUBLISH_PORT = 5556
PUBLISHER_PULL_PORT = 5557

EXPERIMENT_MODEL = 'experimentor.models.experiments.BaseExperiment'
EXPERIMENT_MODEL_INIT = {
    'config_file': 'config.yml',
}

START_WINDOW = 'experimentor.views.DataViewWidget'

PUBLISHER_EXIT_KEYWORD = 'stop'
SUBSCRIBER_EXIT_KEYWORD = 'stop'

GENERAL_STOP_EVENT = Event()

PUBLISHER_READY = False
