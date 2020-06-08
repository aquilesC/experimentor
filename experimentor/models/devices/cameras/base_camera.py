# -*- coding: utf-8 -*-
"""
    Base Camera Model
    =================
    Camera class with the base methods. Having a base class exposes the general API for working with cameras.
    This file is important to keep track of the methods which are exposed to the View.
    The class BaseCamera should be subclassed when developing new Models for other cameras. This ensures that all the
    methods are automatically inherited and there are no breaks downstream.

    Conventions
    -----------
    Images are 0-indexed. Therefore, a camera with (1024px X 1024px) will be used as img[0:1024, 0:1024] (remember
    Python leaves out the last value in the slice.

    Region of Interest is specified with the coordinates of the corners. A full-frame with the example above would be
    given by X=[0,1023], Y=[0,1023]. Be careful, since the maximum width (or height) of the camera is 1024.

    The camera keeps track of the coordinates of the initial pixel. For full-frame, this will always be [0,0]. When
    croping, the corner-pixel will change. It is very important to keep track of this value when building a GUI, since
    after the first crop, if the user wants to crop even further, the information has to be referenced to the already
    cropped area.

    Notes
    -----
    **IMPORTANT** Whatever new function is implemented in a specific model, it should be first declared in the
    BaseCamera class. In this way the other models will have access to the method and the program will keep running
    (perhaps with the wrong behavior though).
"""
import numpy as np

from experimentor import Q_
from experimentor.lib.log import get_logger
from experimentor.models.decorators import not_implemented
from experimentor.models.devices.base_device import ModelDevice
from experimentor.models import Feature


class BaseCamera(ModelDevice):
    """ Base Camera model. All camera models should inherit from this model in order to extend functionality. There are
    some assumptions regarding how to update different settings such as exposure, gain, region of interest.

    Parameters
    ----------
    camera: str or int
        Parameter to identify the camera when loading or initializing it.

    Attributes
    ----------
    AQUISITION_MODE: dict
        Different acquisition modes: Continuous, Single, Keep last.
    cam_num: str or int
        This parameter will be used to identify the camera when loading or initializing it.
    running: bool
        Whether the camera is running or not
    max_width: int
        Maximum width, in pixels
    max_height: int
        Maximum height, in pixels
    data_type: np data type
        The data type of the images generated by the camera. This can be used to allocate the correct amount of memory
        in buffers, or to reduce data before displaying it. For example, ``np.uint16``.
    temp_image: np.array
        It stores the last image acquired by the camera. Useful for user interfaces that need to display images at a
        rate different than the acquisition rate.
    """
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0
    MODE_LAST = 2
    ACQUISITION_MODE = {
        MODE_CONTINUOUS: 'Continuous',
        MODE_SINGLE_SHOT: 'Single',
        MODE_LAST: 'Keep Last',
    }

    camera = 'Base Camera Model'

    def __init__(self, camera):
        super().__init__()
        self.logger = get_logger(__name__)

        self.camera = camera
        self.running = False
        self.data_type = np.uint16
        self.temp_image = None

    def configure(self, properties: dict):
        self.logger.info('Updating config')
        update_cam = False
        update_roi = False
        update_exposure = False
        update_binning = False
        update_gain = False
        for k, new_prop in properties.items():
            self.logger.debug('Updating {} to {}'.format(k, new_prop))

            update_cam = False
            if k in self.config:
                old_prop = self.config[k]
                if new_prop != old_prop:
                    update_cam = True
            else:
                update_cam = True

            if update_cam:
                if k in ['roi_x1', 'roi_x2', 'roi_y1', 'roi_y2']:
                    update_roi = True
                elif k == 'exposure_time':
                    update_exposure = True
                elif k in ['binning_x', 'binning_y']:
                    update_binning = True
                elif k == 'gain':
                    update_gain = True

        if update_cam:
            self.logger.info('There are things to update in the new config')
            if update_roi:
                X = sorted([properties['roi_x1'], properties['roi_x2']])
                Y = sorted([properties['roi_y1'], properties['roi_y2']])
                self.logger.info(f'Updating ROI {X}, {Y}')
                self.set_ROI(X, Y)
                self.config.update({'roi_x1': X[0],
                                    'roi_x2': X[1],
                                    'roi_y1': Y[0],
                                    'roi_y2': Y[1]})

            if update_exposure:
                exposure = properties['exposure_time']
                self.logger.info(f'Updating exposure to {exposure}')
                if isinstance(exposure, str):
                    exposure = Q_(exposure)

                new_exp = self.set_exposure(exposure)
                self.config['exposure_time'] = new_exp

            if update_binning:
                self.logger.info('Updating binning')
                self.set_binning(properties['binning_x'], properties['binning_y'])
                self.config.update({'binning_x': properties['binning_x'],
                                    'binning_y': properties['binning_y']})

            if update_gain:
                self.logger.info(f'Updating gain to {properties["gain"]}')
                self.set_gain(properties['gain'])

    @not_implemented
    def initialize(self):
        """ Initializes the camera. """
        return

    @not_implemented
    def trigger_camera(self):
        """ Triggers the camera. """
        pass

    @Feature()
    @not_implemented
    def acquisition_mode(self):
        """ Set the readout mode of the camera: Single or continuous.
        :param int mode: One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """
        pass

    @acquisition_mode.setter
    def acquisition_mode(self, value):
        pass

    @not_implemented
    def acquisition_ready(self):
        """
        Checks if the acquisition in the camera is over.
        """
        pass

    @Feature()
    @not_implemented
    def exposure(self):
        """ Sets the exposure of the camera. """
        pass

    @exposure.setter
    def exposure(self, value):
        """ Gets the exposure time of the camera. """
        pass

    @not_implemented
    def read_camera(self):
        """ Reads the camera and stores the image in the temp_image attribute
        """
        pass

    @Feature
    @not_implemented
    def ROI(self):
        """ Sets up the ROI. Not all cameras are 0-indexed, so this is an important place to define the proper ROI.

        Values
        ------
        vals : list or tuple
            Organized as (X, Y), where the coordinates for the ROI would be X[0], X[1], Y[0], Y[1]
        """
        pass

    @ROI.setter
    def ROI(self, vals):
        pass

    def clear_ROI(self):
        """ Clears the ROI by setting it to the maximum available area.
        """
        self.ROI = ((0, self.config['max_width']-1), (0, self.config['max_height']-1))

    @Feature()
    @not_implemented
    def serial_number(self):
        """ Returns the serial number of the camera, or a way of identifying the camera in an experiment.
        """
        pass

    @Feature()
    @not_implemented
    def ccd_width(self):
        """ Returns the CCD width in pixels this is equivalent to the :attr:`max_width`
        """
        pass

    @Feature()
    @not_implemented
    def ccd_height(self):
        """ Returns the CCD height in pixels this is equivalent to the :attr:`max_height`
        """
        pass

    @not_implemented
    def stop_acquisition(self):
        """Stops the acquisition without closing the connection to the camera."""
        pass

    @Feature()
    @not_implemented
    def gain(self):
        """Sets the gain on the camera, if possible

        Values
        ------
        gain : float
            The gain, depending on the camera it can be an integer, it can be specified in dB, etc.
        """
        pass

    @gain.setter
    def gain(self, value):
        pass

    @Feature()
    @not_implemented
    def binning(self):
        """ The binning of the camera if supported. Has to check if binning in X/Y can be different or not, etc.

        Values
        ------
        The binning is specified as a list or tuple like: [X, Y], with the information of the binning in the X or Y
        direction.
        """
        pass

    @binning.setter
    def binning(self, values):
        pass

    @not_implemented
    def clear_binning(self):
        """
        Clears the binning of the camera to its default value.
        """
        pass

    @not_implemented
    def stop_camera(self):
        """Stops the acquisition and closes the connection with the camera.
        """
        pass

    def __str__(self):
        return f"Base Camera {self.camera}"
