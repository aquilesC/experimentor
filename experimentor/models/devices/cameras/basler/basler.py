import time
from threading import Event

from pypylon import pylon, _genicam

from experimentor import Q_
from experimentor.lib.log import get_logger
from experimentor.models.cameras.exceptions import WrongCameraState
from experimentor.models.devices.cameras.base_camera import BaseCamera
from experimentor.models.devices.cameras.exceptions import CameraNotFound
# noinspection SpellCheckingInspection
from experimentor.models.model_properties import ModelProp


class BaslerCamera(BaseCamera):
    def __init__(self, camera):
        super().__init__(camera)
        self.logger = get_logger(__name__)
        self.friendly_name = ''
        self._acquisition_mode = self.MODE_SINGLE_SHOT
        self.free_run_running = False
        self._stop_free_run = Event()
        self.fps = 0

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
                self._driver = pylon.InstantCamera()
                self._driver.Attach(tl_factory.CreateDevice(device))
                self._driver.Open()
                self.friendly_name = device.GetFriendlyName()

        if not self._driver:
            msg = f'Basler {self.camera} not found. Please check if the camera is connected'
            self.logger.error(msg)
            raise CameraNotFound(msg)

        self.logger.info(f'Loaded camera {self._driver.GetDeviceInfo().GetModelName()}')

        self._driver.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
                                           pylon.Cleanup_Delete)

        self.config.fetch_all()

    @ModelProp()
    def exposure(self) -> Q_:
        """ The exposure of the camera, defined in units of time """
        try:
            exposure = float(self._driver.ExposureTime.ToString()) * Q_('us')
            return exposure
        except _genicam.TimeoutException:
            self.logger.error('Timeout getting the exposure')
            return self.config['exposure']

    @exposure.setter
    def exposure(self, exposure: Q_):
        self.logger.info(f'Setting exposure to {exposure}')
        try:
            self._driver.ExposureTime.SetValue(exposure.m_as('us'))
        except _genicam.TimeoutException:
            self.logger.error(f'Timed out setting the exposure to {exposure}')

    @ModelProp()
    def gain(self):
        """ Gain is a float """
        try:
            return float(self._driver.Gain.Value)
        except _genicam.TimeoutException:
            self.logger.error('Timeout while reading the gain from the camera')
            return self.config['gain']

    @gain.setter
    def gain(self, gain: float):
        self.logger.info(f'Setting gain to {gain}')
        try:
            self._driver.Gain.SetValue(gain)
        except _genicam.TimeoutException:
            self.logger.error('Problem setting the gain')

    @ModelProp()
    def acquisition_mode(self):
        return self._acquisition_mode

    @acquisition_mode.setter
    def acquisition_mode(self, mode):
        if self._driver.IsGrabbing():
            self.logger.warning(f'{self} Changing acquisition mode for a grabbing camera')

        self.logger.info(f'{self} Setting acquisition mode to {mode}')

        if mode == self.MODE_CONTINUOUS:
            self.logger.debug(f'Setting buffer to {self._driver.MaxNumBuffer.Value}')
            self._acquisition_mode = mode
        elif mode == self.MODE_SINGLE_SHOT:
            self.logger.debug(f'Setting buffer to 1')
            self._acquisition_mode = mode

    @ModelProp()
    def auto_exposure(self):
        """ Auto exposure can take one of three values: Off, Once, Continuous """
        return self._driver.ExposureAuto.Value

    @auto_exposure.setter
    def auto_exposure(self, mode: str):
        modes = ('Off', 'Once', 'Continuous')
        if mode not in modes:
            raise ValueError(f'Mode must be one of {modes} and not {mode}')
        self._driver.ExposureAuto.SetValue(mode)

    @ModelProp()
    def auto_gain(self):
        """ Auto Gain must be one of three values: Off, Once, Continuous"""
        return self._driver.GainAuto.Value

    @auto_gain.setter
    def auto_gain(self, mode):
        modes = ('Off', 'Once', 'Continuous')
        if mode not in modes:
            raise ValueError(f'Mode must be one of {modes} and not {mode}')
        self._driver.GainAuto.SetValue(mode)

    @ModelProp()
    def pixel_format(self):
        """ Pixel format must be one of Mono8, Mono12, Mono12p"""
        return self._driver.PixelFormat.GetValue()

    @pixel_format.setter
    def pixel_format(self, mode):
        self.logger.info(f'Setting pixel format to {mode}')
        self._driver.PixelFormat.SetValue(mode)

    @ModelProp()
    def ROI(self):
        offset_X = self._driver.OffsetX.Value
        offset_Y = self._driver.OffsetY.Value
        width = self._driver.Width.Value - 1
        height = self._driver.Height.Value - 1
        return ((offset_X, offset_X+width),(offset_Y, offset_Y+height))

    @ROI.setter
    def ROI(self, vals):
        X = vals[0]
        Y = vals[1]
        width = int(X[1] - X[1] % 4)
        x_pos = int(X[0] - X[0] % 4)
        height = int(Y[1] - Y[1] % 2)
        y_pos = int(Y[0] - Y[0] % 2)
        self.logger.info(f'Updating ROI: (x, y, width, height) = ({x_pos}, {y_pos}, {width}, {height})')
        self._driver.OffsetX.SetValue(0)
        self._driver.OffsetY.SetValue(0)
        self._driver.Width.SetValue(self.config['max_width'])
        self._driver.Height.SetValue(self.config['max_height'])
        self.logger.debug(f'Setting width to {width}')
        self._driver.Width.SetValue(width)
        self.logger.debug(f'Setting Height to {height}')
        self._driver.Height.SetValue(height)
        self.logger.debug(f'Setting X offset to {x_pos}')
        self._driver.OffsetX.SetValue(x_pos)
        self.logger.debug(f'Setting Y offset to {y_pos}')
        self._driver.OffsetY.SetValue(y_pos)
        self.X = (x_pos, x_pos + width)
        self.Y = (y_pos, y_pos + width)
        self.width = self._driver.Width.Value
        self.height = self._driver.Height.Value

    @ModelProp()
    def ccd_height(self):
        return self._driver.Height.Max

    @ModelProp()
    def ccd_width(self):
        return self._driver.Width.Max

    def __str__(self):
        if self.friendly_name:
            return f"Camera {self.friendly_name}"
        return super().__str__()

    def trigger_camera(self):
        if self._driver.IsGrabbing():
            self.logger.warning('Triggering a grabbing camera')
        self._driver.StopGrabbing()
        mode = self.acquisition_mode
        if mode == self.MODE_CONTINUOUS:
            self._driver.StartGrabbing(pylon.GrabStrategy_OneByOne)
            self.logger.info('Grab Strategy: One by One')
        elif mode == self.MODE_SINGLE_SHOT:
            self._driver.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            self.logger.info('Grab Strategy: Latest Image')
        elif mode == self.MODE_LAST:
            self._driver.StartGrabbing(pylon.GrabStrategy_LatestImages)
        self._driver.ExecuteSoftwareTrigger()
        self.logger.info('Executed Software Trigger')

    def read_camera(self) -> list:
        img = []
        mode = self.acquisition_mode()
        if mode == self.MODE_SINGLE_SHOT or mode == self.MODE_LAST:
            self.logger.info(f'Grabbing mode: {mode}')
            grab = self._driver.RetrieveResult(int(self.get_exposure().m_as('ms')) + 100, pylon.TimeoutHandling_Return)
            if grab and grab.GrabSucceeded():
                img = [grab.GetArray().T]
                grab.Release()
            if mode == self.MODE_SINGLE_SHOT:
                self._driver.StopGrabbing()
            return img
        else:
            if not self._driver.IsGrabbing():
                raise WrongCameraState('You need to trigger the camera before reading')
            num_buffers = self._driver.NumReadyBuffers.Value
            if num_buffers:
                img = [None] * num_buffers
                for i in range(num_buffers):
                    grab = self._driver.RetrieveResult(int(self.exposure.m_as('ms')) + 100, pylon.TimeoutHandling_ThrowException)
                    if grab and grab.GrabSucceeded():
                        img[i] = grab.GetArray().T
                        grab.Release()
                img = [i for i in img if i is not None]
        if len(img) >= 1:
            self.temp_iamge = img[-1]
        return img

    def start_free_run(self):
        """ Starts a free run from the camera. It will preserve only the latest image. It depends
        on how quickly the experiment reads from the camera whether all the images will be available
        or only some.
        """
        if self.free_run_running:
            self.logger.info(f'Trying to start again the free acquisition of camera {self}')
            return
        self.logger.info(f'Starting a free run acquisition of camera {self}')
        self.free_run_running = True
        self.logger.debug('First frame of a free_run')
        self.acquisition_mode = self.MODE_CONTINUOUS
        self.trigger_camera()  # Triggers the camera only once

    def stop_free_run(self):
        self._stop_free_run.set()

    def stop_camera(self):
        self._driver.StopGrabbing()

    def finalize(self):
        self.stop_free_run()
        self.stop_camera()
        self.clean_up_threads()
        super().finalize()


if __name__ == '__main__':
    cam = BaslerCamera('da')
    cam.initialize()
    print(cam.config)
    cam.config['roi'] = ((16, 1200-1), (16, 800-1))
    # print(cam.config.to_update())
    cam.config.apply_all()
    print(cam.config)
    # cam.clear_ROI()
    # cam.config.fetch_all()
    # print(cam.config)
    cam.start_free_run()
    time.sleep(1)
    for i in range(10):
        img = cam.read_camera()
        print(img)