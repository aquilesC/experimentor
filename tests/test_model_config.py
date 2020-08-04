import unittest

from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.exceptions import PropertyException
from experimentor.models.feature import Feature
from experimentor.models.properties import Properties


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
            p = tm.config['param2']  # param1 is not defined until we try to fetch or set its value

        tm.config.fetch_all()
        self.assertEqual(tm.config['param1'], None)

    def test_config_update(self):
        tm = self.test_class()
        tm.config['param1'] = 1
        self.assertEqual(len(tm.config.to_update()), 1)
        self.assertIs(tm.config['param1'], None)
        tm.config.apply_all()
        self.assertEqual(tm.config['param1'], 1)

    def test_new_property(self):
        tm = self.test_class()
        tm.config['new_param'] = 3
        self.assertTrue(tm.config.get_property('new_param')['to_update'])

    def test_update_property(self):
        tm = self.test_class()
        tm.config['param1'] = 123
        self.assertTrue(tm.config.get_property('param1')['to_update'])
        tm.config.apply('param1')
        self.assertFalse(tm.config.get_property('param1')['to_update'])
        tm.config['param1'] = 123
        self.assertTrue(tm.config.get_property('param1')['to_update'])

    def test_get_items(self):
        tm = self.test_class()
        tm.config['param1'] = 123
        tm.config['param2'] = 123
        keys = [list(k.keys())[0] for k in tm.config]
        self.assertIn('param1', keys)
        with self.assertRaises(KeyError):
            tm.config.fetch('wrong key')

    def test_config_dict(self):
        tm = self.test_class()
        config = Properties(tm, **{'param1': 1, 'param2': 2})
        self.assertEqual(config.get_property('param1')['new_value'], 1)
        self.assertEqual(config.get_property('param2')['new_value'], 2)
        self.assertTrue(config.get_property('param1')['to_update'])
        self.assertTrue(config.get_property('param2')['to_update'])

    def test_config_get_all(self):
        tm = self.test_class()
        config = Properties(tm, **{'param1': 1, 'param2': 2})
        all = config.all()
        self.assertIs(all['param1'], None)

    def test_update_config(self):
        tm = self.test_class()
        config = Properties(tm, **{'param1': 1, 'param2': 2})
        config.update({'param1': 10, 'param3': 30})
        self.assertTrue(config.get_property('param1')['to_update'])
        self.assertTrue(config.get_property('param3')['to_update'])
        self.assertEqual(config.get_property('param3')['new_value'], 30)
        self.assertEqual(config.get_property('param1')['new_value'], 10)

    def test_upgrade_config(self):
        tm = self.test_class()
        config = Properties(tm, **{'param1': 1, 'param2': 2})
        config.update({'param1': 10, 'parm3': 30})
        with self.assertRaises(PropertyException):
            config.upgrade({'param4': 10})

        config.upgrade({'param4': 40}, force=True)
        self.assertEqual(config['param4'], 40)

    def test_property_setter(self):
        class PropertyTest(ModelDevice):
            def __init__(self):
                super().__init__()
                self._param = None
                self.config.link({'param': ['param', 'param']})

            @property
            def param(self):
                return self._param

            @param.setter
            def param(self, value):
                self._param = value

        pt = PropertyTest()
        pt.param = 10
        pt.config.fetch_all()
        pt.config.update({'param': 10})
        pt.config.apply_all()
        self.assertEqual(pt.param, pt.config['param'])
        self.assertEqual(pt.param, 10)
        self.assertEqual(pt.config['param'], 10)

    def test_unlink(self):
        tm = self.test_class()
        tm.config.unlink(['param1', ])
        self.assertIsNone(tm.config._links['param1'])
        with self.assertWarns(Warning):
            tm.config.unlink(['param2', ])

    def test_from_dict(self):
        tm = self.test_class()
        config = Properties.from_dict(tm, {'param1': [1, 'get_param1', 'set_param1']})
        self.assertEqual(config.get_property('param1')['new_value'], 1)