import unittest

from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.feature import Feature


class TestModelProps(unittest.TestCase):
    def setUp(self) -> None:
        class TestModel(ModelDevice):
            _param = None

            def __init__(self):
                super().__init__()
                self.param = 1

            @Feature()
            def param(self):
                return self._param

            @param.setter
            def param(self, val):
                self._param = val

            @Feature()
            def only_get(self):
                return 1

            @Feature
            def with_call(self):
                return 2

            @with_call
            def with_call(self, val):
                pass

        self.test_model = TestModel

    def test_setting(self):
        tm = self.test_model()
        tm.param = 2
        tm.config.fetch_all()
        self.assertEqual(tm.param, tm.config['param'])

    def test_to_update(self):
        tm = self.test_model()
        tm.config['param'] = 3
        self.assertTrue(tm.config.get_property('param')['to_update'])
        self.assertEqual(tm.config.get_property('param')['new_value'], 3)

    def test_apply_all(self):
        tm = self.test_model()
        tm.config['param'] = 3
        tm.config.apply_all()
        self.assertFalse(tm.config.get_property('param')['to_update'])
        self.assertEqual(tm.param, tm.config.get_property('param')['value'])
