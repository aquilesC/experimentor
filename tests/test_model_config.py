import unittest

from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.model_properties import ModelProp


class TestModelCreation(unittest.TestCase):
    def setUp(self) -> None:
        class TestModel(ModelDevice):
            def __init__(self):
                super().__init__()
                self._param1 = None

                self.config.link({
                    'param1': ['get_param1', 'set_param1']
                })

            def set_param1(self, val):
                self._param1 = val

            def get_param1(self):
                return self._param1
        self.test_class = TestModel

    def test_config_values(self):
        tm = self.test_class()
        with self.assertRaises(KeyError):
            p = tm.config['param1']  # param1 is not defined until we try to fetch or set its value

        tm.config.fetch_all()
        self.assertEqual(tm.config['param1'], None)

    def test_config_update(self):
        tm = self.test_class()
        tm.config['param1'] = 1
        self.assertEqual(len(tm.config.to_update()), 1)
        self.assertIs(tm.config['param1'], None)
        tm.config.apply_all()
        self.assertEqual(tm.config['param1'], 1)

    def test_model_prop(self):
        class TestModel(ModelDevice):
            def __init__(self):
                super().__init__()
                self._param = 0
                self.param = 1
                self.config.autolink()

            @ModelProp()
            def param(self):
                return self._param

            @param.setter
            def param(self, val):
                self._param = val

        tm = TestModel()
        print(tm.config._links)
        self.assertTrue(hasattr(tm, 'config'))
        tm.config.fetch_all()
        print(tm.config._links)
        self.assertEqual(tm.param, 1)
        self.assertEqual(tm.config['param'], 1)
        print(tm.config._links)
        tm.param = 2
        self.assertEqual(tm.param, 2)
        self.assertEqual(tm.config['param'], tm.param)

        tm.config['param'] = 3
        print(tm.config.to_update())
        print(tm.config._links)
        print(TestModel.config._links)
        print(tm.config)
