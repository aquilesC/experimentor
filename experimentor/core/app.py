import importlib
import logging
from threading import Thread

from experimentor.config import settings
from experimentor.core import Publisher
from experimentor.core.meta import ExperimentorProcess
from experimentor.lib.log import get_logger, log_to_screen
from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.experiments.base_experiment import BaseExperiment


class ExperimentApp:
    def __init__(self, ExperimentModel=None, initialize=True, gui=False, rehook_publisher=False, logger=logging.INFO):
        self.log = get_logger()
        if logger:
            handler = log_to_screen(logger=self.log,level=logger)
        self.log.info(f'Experiment Model: {settings.EXPERIMENT_MODEL}')
        if not ExperimentModel:
            exp_model = settings.EXPERIMENT_MODEL.split('.')
            experiment_module = importlib.import_module('.'.join(exp_model[:-1]))
            experiment_model_class = getattr(experiment_module, exp_model[-1])
        else:
            experiment_model_class = ExperimentModel
        if settings.EXPERIMENT_MODEL_INIT is not None:
            self.experiment_model = experiment_model_class(**settings.EXPERIMENT_MODEL_INIT)
        else:
            self.experiment_model = experiment_model_class()

        if initialize:
            self.experiment_model.initialize()

        if not rehook_publisher:
            self.publisher = Publisher(settings.GENERAL_STOP_EVENT)
            self.publisher.start()

        self.gui_thread = False
        if gui:
            self.gui_thread = Thread(target=start_gui, args=(self.experiment_model, ))
            self.gui_thread.start()

    @property
    def is_running(self):
        if self.gui_thread :
            if self.gui_thread.is_alive():
                return True
            else:
                return False
        if self.experiment_model.is_alive:
            return True

    def finalize(self):
        experiments = BaseExperiment.get_instances(recursive=True)
        self.log.info(f'{len(experiments)} Experiments defined in the app. Trying to stop them.')
        for exp in experiments:
            try:
                exp.finalize()
            except:
                self.log.error(f'Could not finalize {exp}')

        devices = ModelDevice.get_instances(recursive=True)
        self.log.info(f'{len(devices)} Model devices defined in the app. Trying to stop them.')
        for dev in devices:
            try:
                dev.finalize()
            except:
                self.log.error(f'Couldn\'t finalize {dev}')

        self.log.info('Stopping publisher')
        self.publisher.stop()

        processes = ExperimentorProcess.get_instances(recursive=True)
        processes = [proc for proc in processes if proc.is_alive()]
        if len(processes):
            self.log.error('There are still {len(processes)} alive. They should have been stopped by now')

        self.log.info('Bye Bye!')


def start_gui(experiment_model):
    from PyQt5.QtWidgets import QApplication

    gui_app = QApplication([])

    win_module = settings.START_WINDOW.split('.')
    window_module = importlib.import_module('.'.join(win_module[:-1]))
    window_class = getattr(window_module, win_module[-1])

    gui_start_window = window_class(experiment_model)
    gui_start_window.show()
    gui_app.exec()