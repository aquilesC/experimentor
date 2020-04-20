import importlib
from multiprocessing.context import Process
from threading import Thread

from experimentor.config import settings
from experimentor.core import Publisher


class ExperimentApp:
    def __init__(self, initialize=True, gui=False, rehook_publisher=False):
        exp_model = settings.EXPERIMENT_MODEL.split('.')
        experiment_module = importlib.import_module('.'.join(exp_model[:-1]))
        experiment_model_class = getattr(experiment_module, exp_model[-1])
        self.experiment_model = experiment_model_class(**settings.EXPERIMENT_MODEL_INIT)

        if initialize:
            self.experiment_model.initialize()

        if not rehook_publisher:
            self.publisher = Publisher(settings.GENERAL_STOP_EVENT)
            self.publisher.start()

        if gui:
            self.gui_thread = Thread(target=start_gui, args=(self.experiment_model, ))
            self.gui_thread.start()

    @property
    def is_running(self):
        if self.experiment_model.is_alive:
            return True


def start_gui(experiment_model):
    from PyQt5.QtWidgets import QApplication

    gui_app = QApplication([])

    win_module = settings.START_WINDOW.split('.')
    window_module = importlib.import_module('.'.join(win_module[:-1]))
    window_class = getattr(window_module, win_module[-1])

    gui_start_window = window_class(experiment_model)
    gui_start_window.show()
    gui_app.exec()
    experiment_model.finalize()