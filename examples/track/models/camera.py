from examples.track.controllers.fake_cam import FakeCam
from experimentor.models import Camera


class MyCamera(Camera):
    __driver__ = FakeCam

    def initialize(self):
        self.dr