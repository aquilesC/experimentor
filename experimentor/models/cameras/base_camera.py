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
    Images are 0-indexed. Therefore, a camera with 1024pxx1024px will be used as img[0:1024, 0:1024] (remember Python
    leaves out the last value in the slice.

    Region of Interest is specified with the coordinates of the corners. A full-frame with the example above would be
    given by X=[0,1023], Y=[0,1023]. Be careful, since the maximum width (or height) of the camera is 1024.

    The camera keeps track of the coordinates of the initial pixel. For full-frame, this will always be [0,0]. When this
    is very important for the GUI, since after the first crop, if the user wants to crop even further, the information
    has to be referenced to the already cropped area.


    .. note:: **IMPORTANT** Whatever new function is implemented in a specific model, it should be first declared in the BaseCamera class. In this way the other models will have access to the method and the program will keep running (perhaps with non intended behavior though).

    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details
"""
import numpy as np

from pynta.model.decorators import not_implemented
from pynta.util.log import get_logger
from pynta import Q_


logger = get_logger(__name__)


class BaseCamera:
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0
    ACQUISITION_MODE = {
        MODE_CONTINUOUS: 'Continuous',
        MODE_SINGLE_SHOT: 'Single'
    }

    def __init__(self, camera):
        self.cam_num = camera
        self.running = False
        self.max_width = 0
        self.max_height = 0
        self.exposure = 0
        self.config = {}
        self.data_type = np.uint16 # The data type that the camera generates when acquiring images. It is very important to have it available in order to create the buffer and saving to disk.

        self.logger = get_logger(name=__name__)

    def configure(self, properties: dict):
        self.logger.info('Updating config')
        update_cam = False
        update_roi = False
        update_exposure = False
        update_binning = False
        for k, new_prop in properties.items():
            self.logger.debug('Updating {} to {}'.format(k, new_prop))

            update_cam = True
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

        if update_cam:
            if update_roi:
                X = sorted([properties['roi_x1'], properties['roi_x2']])
                Y = sorted([properties['roi_y1'], properties['roi_y2']])
                self.set_ROI(X, Y)
                self.config.update({'roi_x1': X[0],
                                    'roi_x2': X[1],
                                    'roi_y1': Y[0],
                                    'roi_y2': Y[1]})

            if update_exposure:
                exposure = properties['exposure_time']
                if isinstance(exposure, str):
                    exposure = Q_(exposure)

                new_exp = self.set_exposure(exposure)
                self.config['exposure_time'] = new_exp

            if update_binning:
                self.set_binning(properties['binning_x'], properties['binning_y'])
                self.config.update({'binning_x': properties['binning_x'],
                                    'binning_y': properties['binning_y']})

    @not_implemented
    def initialize(self):
        """
        Initializes the camera.
        """
        self.max_width = self.GetCCDWidth()
        self.max_height = self.GetCCDHeight()
        return True

    @not_implemented
    def trigger_camera(self):
        """
        Triggers the camera.
        """
        pass

    @not_implemented
    def set_acquisition_mode(self, mode):
        """
        Set the readout mode of the camera: Single or continuous.
        :param int mode: One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        :return:
        """
        self.mode = mode

    def get_acquisition_mode(self):
        """
        Returns the acquisition mode, either continuous or single shot.
        """
        return self.mode

    @not_implemented
    def acquisition_ready(self):
        """
        Checks if the acquisition in the camera is over.
        """
        pass

    @not_implemented
    def set_exposure(self, exposure):
        """
        Sets the exposure of the camera.
        """
        self.exposure = exposure

    @not_implemented
    def get_exposure(self):
        """
        Gets the exposure time of the camera.
        """
        return self.exposure

    @not_implemented
    def read_camera(self):
        """
        Reads the camera
        """
        pass

    @not_implemented
    def set_ROI(self, X, Y):
        """ Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.

        :param list X: array type with the coordinates for the ROI X[0], X[1]
        :param list Y: array type with the coordinates for the ROI Y[0], Y[1]
        :return: X, Y lists with the current ROI information
        """
        return X, Y


    def clear_ROI(self):
        """
        Clears the ROI from the camera.
        """
        self.set_ROI([0, self.max_width], [0, self.max_height])

    @not_implemented
    def get_size(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        pass

    @not_implemented
    def getSerialNumber(self):
        """Returns the serial number of the camera.
        """
        pass

    @not_implemented
    def GetCCDWidth(self):
        """
        Returns the CCD width in pixels
        """
        pass

    @not_implemented
    def GetCCDHeight(self):
        """
        Returns: the CCD height in pixels
        """
        pass

    @not_implemented
    def stopAcq(self):
        """Stops the acquisition without closing the connection to the camera."""
        pass

    @not_implemented
    def set_binning(self, xbin, ybin):
        """
        Sets the binning of the camera if supported. Has to check if binning in X/Y can be different or not, etc.

        :param xbin:
        :param ybin:
        :return:
        """
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
