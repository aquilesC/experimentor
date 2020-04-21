import unittest

from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.devices.cameras.base_camera import BaseCamera
from experimentor.models.models import BaseModel


class TestDeviceModel(unittest.TestCase):
    def test_model_device(self):
        dev = ModelDevice()
        self.assertEqual(f"Model {id(dev)}", f"{dev}")
        
    def test_model_camera(self):
        cam = BaseCamera('cam')
        self.assertIsInstance(cam, BaseModel)
        self.assertEqual('cam', cam.camera)
