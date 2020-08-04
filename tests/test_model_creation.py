import unittest
from time import sleep

from experimentor.core.exceptions import ModelDefinitionException
from experimentor.core.signal import Signal
from experimentor.models.decorators import make_async_thread
from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.models import MetaModel, BaseModel


class TestModelCreation(unittest.TestCase):
    def test_signal_creation(self):
        class TestModel(BaseModel):
            signal = Signal()

        self.assertTrue(hasattr(TestModel, '_signals'))

    def test_signals_model(self):
        class TestModel(BaseModel):
            a1 = Signal()
            a2 = Signal()

        tm = TestModel()
        self.assertIs(len(tm._signals), 2)

    def test_get_model_instances(self):
        class TestModel(metaclass=MetaModel):
            pass

        tm = TestModel()
        tm_2 = TestModel()

        self.assertIs(len(TestModel.get_models()), 1)
        self.assertIs(len(TestModel.get_instances()), 2)

    def test_get_model_instances_recursive(self):
        class TestModel(metaclass=MetaModel):
            pass

        class OtherTest(TestModel):
            pass

        tm = TestModel()
        otm = OtherTest()

        self.assertIs(len(TestModel.get_models()), 1)
        self.assertIs(len(OtherTest.get_models()), 1)
        self.assertIs(len(TestModel.get_instances()), 1)
        self.assertIs(len(TestModel.get_models(recursive=True)), 2)
        self.assertIs(len(TestModel.get_instances(recursive=True)), 2)

    def test_clean_thread(self):
        class TestModel(BaseModel):
            @make_async_thread
            def simple_func(self):
                return True

        tm = TestModel()
        tm.simple_func()
        self.assertEqual(len(tm._threads), 1)
        tm.clean_up_threads()
        self.assertEqual(len(tm._threads), 0)
