import unittest

from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.model_properties import ModelProp


class TestModel(ModelDevice):
    def __init__(self):
        super().__init__()
        self._param = 0
        self.param = 1


    @ModelProp()
    def param(self):
        return self._param

    @param.setter
    def param(self, val):
        self._param = val

tm = TestModel()


class TestModelProps(unittest.TestCase):
    def test_setting(self):
        tm.param = 2
        tm.config.fetch_all()
        self.assertEqual(tm.param, tm.config['param'])

    def test_to_update(self):
        tm.config['param'] = 3
        self.assertTrue(tm.config.get_property('param')['to_update'])
        self.assertEqual(tm.config.get_property('param')['new_value'], 3)

    def test_apply_all(self):
        tm.config['param'] = 3
        tm.config.apply_all()
        self.assertFalse(tm.config.get_property('param')['to_update'])
        self.assertEqual(tm.param, tm.config.get_property('param')['value'])
