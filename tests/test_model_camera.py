import logging
import unittest

from experimentor.lib.log import get_logger
from experimentor.models.devices.cameras.base_camera import BaseCamera


class TestDeviceModel(unittest.TestCase):
    def test_model_camera_not_implemented(self):
        class Camera(BaseCamera):
            def __init__(self, camera):
                super().__init__(camera)

        cam = Camera('cam')
        log = get_logger()
        with self.assertLogs(logger=log, level=logging.WARNING):
            cam.config.fetch_all()