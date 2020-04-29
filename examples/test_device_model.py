import unittest

from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.devices.cameras.base_camera import BaseCamera
from experimentor.models.models import BaseModel


class TestDeviceModel(unittest.TestCase):
    def test_model_device(self):
        dev = ModelDevice()
        self.assertIsInstance(dev, BaseModel)
        self.assertEqual(f"Model {id(dev)}", f"{dev}")
        self.assertTrue(hasattr(dev, 'config'))
        
    def test_model_camera(self):
        cam = BaseCamera('cam')
        self.assertIsInstance(cam, ModelDevice)
        self.assertEqual('cam', cam.camera)
