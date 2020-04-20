from pypylon import pylon, _genicam

from experimentor import Q_
from experimentor.lib.log import get_logger
from experimentor.models.devices.cameras.base_camera import BaseCamera
from experimentor.models.devices.cameras.exceptions import CameraNotFound


class BaslerCamera(BaseCamera):
    def __init__(self, camera):
        super().__init__(camera)
        self.logger = get_logger(__name__)
        self.friendly_name = ''

    def initialize(self):
        """ Initializes the communication with the camera. Get's the maximum and minimum width. It also forces
        the camera to work on Software Trigger.

        .. warning:: It may be useful to integrate other types of triggers in applications that need to
            synchronize with other hardware.

        """
        self.logger.debug('Initializing Basler Camera')
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()
        if len(devices) == 0:
            raise CameraNotFound('No camera found')

        for device in devices:
            if self.camera in device.GetFriendlyName():
                self.camera = pylon.InstantCamera()
                self.camera.Attach(tl_factory.CreateDevice(device))
                self.camera.Open()
                self.friendly_name = device.GetFriendlyName()

        if not self.camera:
            msg = f'{self.camera} not found. Please check your config file and cameras connected'
            self.logger.error(msg)
            raise CameraNotFound(msg)

        self.logger.info(f'Loaded camera {self.camera.GetDeviceInfo().GetModelName()}')

        self.camera.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
                                          pylon.Cleanup_Delete)

        self.config.fetch_all()

    def get_exposure(self) -> Q_:
        try:
            exposure = float(self.camera.ExposureTime.ToString()) * Q_('us')
            return exposure
        except _genicam.TimeoutException:
            self.logger.error('Timeout getting the exposure')
            return self.config['exposure']

    def set_exposure(self, exposure: Q_):
        self.camera.ExposureTime.SetValue(exposure.m_as('us'))

    def set_gain(self, gain: float):
        self.logger.info(f'Setting gain to {gain}')
        try:
            self.camera.Gain.SetValue(gain)
        except _genicam.RuntimeException:
            self.logger.error('Problem setting the gain')

    def get_gain(self) -> float:
        try:
            self.gain = float(self.camera.Gain.Value)
            return self.gain
        except _genicam.TimeoutException:
            self.logger.error('Timeout while reading the gain from the camera')
            return self.config['gain']