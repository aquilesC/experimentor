# noinspection SpellCheckingInspection

from multiprocessing import Lock

import numpy as np
import time
from threading import Event

from pypylon import pylon, _genicam

from experimentor import Q_
from experimentor.core.signal import Signal
from experimentor.lib.log import get_logger
from experimentor.models.action import Action
from experimentor.models.decorators import make_async_thread
from experimentor.models.devices.cameras.exceptions import WrongCameraState, CameraException
from experimentor.models.devices.cameras.base_camera import BaseCamera
from experimentor.models.devices.cameras.exceptions import CameraNotFound
from experimentor.models import Feature


class BaslerCamera(BaseCamera):
    _acquisition_mode = BaseCamera.MODE_SINGLE_SHOT
    new_image = Signal()
    _basler_lock = Lock()

    def __init__(self, camera, initial_config=None):
        super().__init__(camera, initial_config=initial_config)
        self.logger = get_logger(__name__)
        self.friendly_name = ''
        self.free_run_running = False
        self._stop_free_run = Event()
        self.fps = 0
        self.keep_reading = False
        self.continuous_reads_running = False
        self.finalized = False
        self._buffer_size = None
        self.current_dtype = None

    @Feature()
    def buffer_size(self):
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value):
        value = Q_(value)
        self.logger.info(f'{self} - Setting buffer size to {value}')
        self._buffer_size = value

    @Action
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

        # self._driver.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
        #                                    pylon.Cleanup_Delete)

        self.config.fetch_all()
        if self.initial_config is not None:
            self.config.update(self.initial_config)
            self.config.apply_all()

    @Feature()
    def exposure(self) -> Q_:
        """ The exposure of the camera, defined in units of time """
        if self.config['exposure'] is not None:
            return self.config['exposure']
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
            if not isinstance(exposure, Q_):
                exposure = Q_(exposure)
            self._driver.ExposureTime.SetValue(exposure.m_as('us'))
            exposure = float(self._driver.ExposureTime.ToString()) * Q_('us')
            self.config.upgrade({'exposure': exposure})
        except _genicam.TimeoutException:
            self.logger.error(f'Timed out setting the exposure to {exposure}')

    @Feature()
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

    @Feature()
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

    @Feature()
    def auto_exposure(self):
        """ Auto exposure can take one of three values: Off, Once, Continuous """
        return self._driver.ExposureAuto.Value

    @auto_exposure.setter
    def auto_exposure(self, mode: str):
        modes = ('Off', 'Once', 'Continuous')
        if mode is False:
            mode = 'Off'
        if mode is True:
            mode = 'Once'

        if mode not in modes:
            raise ValueError(f'Mode must be one of {modes} and not {mode}')
        self._driver.ExposureAuto.SetValue(mode)

    @Feature()
    def binning_y(self):
        self.logger.debug('Retrieving binningY')
        return self._driver.BinningVertical.Value

    @binning_y.setter
    def binning_y(self, value):
        if value not in range(1, 5):
            raise CameraException('BinningY must be one of (1, 2, 3, 4) pixels')
        self.logger.info(f'Setting BinningY to {value}')
        self._driver.BinningVertical.SetValue(value)

    @Feature()
    def binning_x(self):
        self.logger.debug('Retrieving binningX')
        return self._driver.BinningVertical.Value

    @binning_x.setter
    def binning_x(self, value):
        if value not in range(1, 5):
            raise CameraException('BinningX must be one of (1, 2, 3, 4) pixels')
        self.logger.info(f'Setting BinningX to {value}')
        self._driver.BinningHorizontal.SetValue(value)

    @Feature()
    def auto_gain(self):
        """ Auto Gain must be one of three values: Off, Once, Continuous"""
        return self._driver.GainAuto.Value

    @auto_gain.setter
    def auto_gain(self, mode):
        modes = ('Off', 'Once', 'Continuous')
        if mode is False:
            mode = 'Off'
        if mode is True:
            mode = 'Once'
        if mode not in modes:
            raise ValueError(f'Mode must be one of {modes} and not {mode}')
        self._driver.GainAuto.SetValue(mode)

    @Feature()
    def pixel_format(self):
        """ Pixel format must be one of Mono8, Mono12, Mono12p"""
        pixel_format = self._driver.PixelFormat.GetValue()
        if pixel_format == 'Mono8':
            self.current_dtype = np.uint8
        elif pixel_format == 'Mono12' or pixel_format == 'Mono12p':
            self.current_dtype = np.uint16
        else:
            self.logger.warning(f'Current pixel format is {pixel_format} while only Mono8, Mono12 and Mono12p are supported')
        return pixel_format

    @pixel_format.setter
    def pixel_format(self, mode):
        self.logger.info(f'Setting pixel format to {mode}')
        self._driver.PixelFormat.SetValue(mode)
        if mode == 'Mono8':
            self.current_dtype = np.uint8
        elif mode == 'Mono12' or mode == 'Mono12p':
            self.current_dtype = np.uint16
        else:
            self.logger.warning(f'Trying to set pixel_format to {mode}, which is not valid')

    @Feature()
    def width(self):
        return self._driver.Width.Value

    @Feature()
    def height(self):
        return self._driver.Height.Value

    @Feature()
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

        self._driver.Width.SetValue(self._driver.WidthMax.GetValue())
        self._driver.Height.SetValue((self._driver.HeightMax.GetValue()))
        self.logger.debug(f'Setting width to {width}')
        self._driver.Width.SetValue(width)
        self.logger.debug(f'Setting Height to {height}')
        self._driver.Height.SetValue(height)
        self.logger.debug(f'Setting X offset to {x_pos}')
        self._driver.OffsetX.SetValue(x_pos)
        self.logger.debug(f'Setting Y offset to {y_pos}')
        self._driver.OffsetY.SetValue(y_pos)
        self.X = (x_pos, x_pos + width)
        self.Y = (y_pos, y_pos + height)

    @Feature()
    def ccd_height(self):
        return self._driver.Height.Max

    @Feature()
    def ccd_width(self):
        return self._driver.Width.Max

    def __str__(self):
        if self.friendly_name:
            return f"Camera {self.friendly_name}"
        return super().__str__()

    def trigger_camera(self):
        self.logger.info(f'Triggering {self} with mode: {self.acquisition_mode}')
        if self._driver.IsGrabbing():
            self.logger.warning('Triggering a grabbing camera')
            self._driver.StopGrabbing()
        mode = self.acquisition_mode
        if mode == self.MODE_CONTINUOUS:
            self.logger.info(f'{self} - Triggering Continuous, {self.current_dtype}')#, frame: ({self.width},{self.height})')
            # Calculate frame size in bytes
            if self.current_dtype == np.uint8:
                frame_size = self.width*self.height
            elif self.current_dtype == np.uint16:
                frame_size = self.width*self.height*2
            else:
                raise CameraException(f'{self} frame dtype is not known to allocate the buffer')

            # Calculate the number of frames to be allocated based on the buffer size (in MB) and the frame size
            # This is useful to keep into account that the frame can be cropped via the ROI or Binning.
            self.logger.info(f'{self} - Frame size: {frame_size} bytes')
            max_buffer_size = int(self.buffer_size.m_as('byte')/frame_size)
            self.logger.info(f'{self} - Calculated max buffer {max_buffer_size}')

            self._driver.MaxNumBuffer = max_buffer_size
            self._driver.OutputQueueSize = self._driver.MaxNumBuffer.Value
            self._driver.StartGrabbing(pylon.GrabStrategy_OneByOne)
            self.logger.info('Grab Strategy: One by One')
            self.logger.info(f'Output Queue Size: {self._driver.MaxNumBuffer.Value}')
        elif mode == self.MODE_SINGLE_SHOT:
            self._driver.MaxNumBuffer = 1
            self._driver.OutputQueueSize = 1
            self._driver.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            self.logger.info('Grab Strategy: Latest Image')
        elif mode == self.MODE_LAST:
            self._driver.MaxNumBuffer = 10
            self._driver.OutputQueueSize = self._driver.MaxNumBuffer.Value
            self._driver.StartGrabbing(pylon.GrabStrategy_LatestImages)
            self.logger.info('Grab Strategy: Latest Images')
        else:
            raise CameraException('Unknown acquisition mode')

        # self._driver.ExecuteSoftwareTrigger()
        self.logger.info('Executed Software Trigger')
        self.config.fetch_all()

    # @Action
    def read_camera(self) -> list:
        with self._basler_lock:
            img = []
            mode = self.acquisition_mode
            self.logger.debug(f'Grabbing mode: {mode}')
            if mode == self.MODE_SINGLE_SHOT or mode == self.MODE_LAST:
                grab = self._driver.RetrieveResult(int(self.exposure.m_as('ms')) + 100, pylon.TimeoutHandling_Return)
                if grab and grab.GrabSucceeded():
                    img = [grab.GetArray().T]
                    self.temp_image = img[0]
                    grab.Release()
                if mode == self.MODE_SINGLE_SHOT:
                    self._driver.StopGrabbing()
                return img
            else:
                if not self._driver.IsGrabbing():
                    raise WrongCameraState('You need to trigger the camera before reading')
                num_buffers = self._driver.NumReadyBuffers.Value
                if num_buffers > 0:
                    if num_buffers > 0.9*self._driver.OutputQueueSize.Value:
                        self.logger.warning(f'{self} Buffer filled to 90% num buffers: {num_buffers}')
                    img = [np.zeros((self.width, self.height), dtype=self.current_dtype)] * num_buffers
                    tot_frames = 0
                    for i in range(num_buffers):
                        grab = self._driver.RetrieveResult(int(self.exposure.m_as('ms')) + 100, pylon.TimeoutHandling_ThrowException)
                        if grab:
                            if grab.GrabSucceeded():
                                img[i] = grab.GetArray().T
                                grab.Release()
                                tot_frames += 1
                            else:
                                self.logger.warning(f'{self}: Grabbing failed {grab.ErrorDescription}')
                        if i > 1:
                            if np.all(img[i] == img[i-1]) and len(np.nonzero(img[i])[0]) > 0:
                                self.logger.error(f'{self}: Duplicated frames grabbed from Basler')
                        # else:
                        #     if np.any(self.temp_image):
                        #         if np.all(self.temp_image == img[i]):
                        #             self.logger.error('Duplicated frame grabbed from Basler')
                    if tot_frames != num_buffers:
                        self.logger.warning(f'{self}: Number of buffers: {num_buffers} but number of frames read: {tot_frames}')
                    img = img[:tot_frames]
            if len(img) >= 1:
                self.temp_image = img[-1]

            return img

    @make_async_thread
    def continuous_reads(self):
        self.continuous_reads_running = True
        self.keep_reading = True
        while self.keep_reading:
            imgs = self.read_camera()
            if len(imgs) >= 1:
                for img in imgs:
                    self.new_image.emit(img)
            time.sleep(.001)
        self.continuous_reads_running = False

    def stop_continuous_reads(self):
        self.keep_reading = False
        while self.continuous_reads_running:
            time.sleep(.1)
        self.logger.info(f'{self} - Stopped continuous reads')

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

    @Feature()
    def frame_rate(self):
        return float(self._driver.ResultingFrameRate.Value)

    @Action
    def stop_free_run(self):
        self._driver.StopGrabbing()
        self.free_run_running = False

    @Action
    def stop_camera(self):
        self._driver.StopGrabbing()

    def finalize(self):
        self.logger.info(f'Finalizing camera {self}')
        if self.finalized:
            return

        self.stop_continuous_reads()
        self.stop_free_run()

        self.stop_camera()
        while self.continuous_reads_running:
            time.sleep(.1)

        super(BaslerCamera, self).finalize()
        self.finalized = True


if __name__ == '__main__':
    cam = BaslerCamera('da')
    cam.initialize()
    cam.exposure = Q_('100ms')
    print(cam.exposure)
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