import os
import sys
import unittest
from time import sleep


class TestExperimentApp(unittest.TestCase):
    def test_app(self):
        os.environ.setdefault("EXPERIMENTOR_SETTINGS_MODULE", "settings")

        this_dir = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(this_dir)

        from experimentor.core.app import ExperimentApp

        app = ExperimentApp(gui=False, logger=False)
        while app.is_running:
            sleep(5)
            app.experiment_model.finalize()
        app.finalize()