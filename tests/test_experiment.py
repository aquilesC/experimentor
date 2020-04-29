import os
import unittest

from experimentor.models.experiments.base_experiment import Experiment


class TestExperimentModel(unittest.TestCase):
    def test_config(self):
        class Exp(Experiment):
            pass
        exp = Exp()
        self.assertTrue(hasattr(exp, 'config'))
        exp.stop_subscribers()
        exp.finalize()

    def test_make_folder(self):
        folder, filename = Experiment.make_filename('.', '{i}.dat')
        folder = os.path.abspath(folder)
        this_folder = os.getcwd()
        self.assertEqual(folder, this_folder)
        self.assertEqual('0.dat', filename)