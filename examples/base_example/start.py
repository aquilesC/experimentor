import logging
import os
import sys
from time import sleep


if __name__ == "__main__":
    os.environ.setdefault("EXPERIMENTOR_SETTINGS_MODULE", "settings")

    this_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(this_dir)

    from experimentor.core.app import ExperimentGuiApp

    app = ExperimentGuiApp(experiment_model=ExperimentGuiApp,logger=logging.DEBUG)
    print('Created App')
    sleep(5)
    print('Emiting signal')
    app.experiment_model.signal.emit('a')
    while app.is_running:
        sleep(5)
        app.experiment_model.finalize()