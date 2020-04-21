import unittest

from experimentor.core.exceptions import ModelDefinitionException
from experimentor.core.signal import Signal
from experimentor.models.models import MetaModel, BaseModel


class TestModelCreation(unittest.TestCase):
    def test_error_class_definition(self):
        with self.assertRaises(ModelDefinitionException):
            class TestModel(metaclass=MetaModel):
                _signals = []

    def test_signal_creation(self):
        class TestModel(metaclass=MetaModel):
            signal = Signal()

        self.assertTrue(hasattr(TestModel, '_signals'))

    def test_signals_attribute(self):
        with self.assertWarns(UserWarning):
            class TestModel(metaclass=MetaModel):
                pass
            TestModel.signals = []
            tm = TestModel()

    def test_signals_model(self):
        class TestModel(metaclass=MetaModel):
            a1 = Signal()
            a2 = Signal()

        tm = TestModel()
        self.assertIs(len(tm.signals), 2)

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

    def test_model_proxy(self):
        class TestModel(BaseModel):
            pass

        tm = TestModel.as_process()

        self.assertTrue(hasattr(tm, 'child_process'))