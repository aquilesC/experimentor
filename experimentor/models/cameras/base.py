"""
    UUTrack.Model.Cameras._skeleton.py
    ==================================
    Camera class with the skeleton functions. Important to keep track of the methods that are
    exposed to the View. The class cameraBase should be subclassed when developing new Models. This ensures that all the methods are automatically inherited and there is no breaks downstream.

    .. note:: **IMPORTANT** Whatever new function is implemented in a specific model, it should be first declared in the cameraBase class. In this way the other models will have access to the method and the program will keep running (perhaps with non intended behavior though).

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""
from ..models import Model


class cameraBase(Model):
    _driver = None
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0

    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.running = False
        self.maxWidth = 0
        self.maxHeight = 0
        self.exposure = 0

    def initialize(self):
        """
        Initializes the camera.
        """
        self.maxWidth = self.GetCCDWidth()
        self.maxHeight = self.GetCCDHeight()
        return True

    def trigger_camera(self):
        """
        Triggers the camera.
        """
        raise Exception("trigger camera Not Implemented")

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

    def acquisition_ready(self):
        """
        Checks if the acquisition in the camera is over.
        """
        raise Exception('acquisition_ready not yet implemented')

    def set_exposure(self, exposure):
        """
        Sets the exposure of the camera.
        """
        self.exposure = exposure
        raise Exception("Not Implemented")

    def get_exposure(self):
        """
        Gets the exposure time of the camera.
        """
        raise Exception("Not Implemented")
        return self.exposure
        
    def read_camera(self):
        """
        Reads the camera
        """
        print("Not Implemented")

    def setROI(self,X,Y):
        """ Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.

        :param array X: array type with the coordinates for the ROI X[0], X[1]
        :param array Y: array type with the coordinates for the ROI Y[0], Y[1]
        :return:
        """
        print("Not Implemented")

    def clearROI(self):
        """
        Clears the ROI from the camera.
        """
        self.setROI(self.maxWidth, self.maxHeight)

    def getSize(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        print("Not Implemented")

    def getSerialNumber(self):
        """Returns the serial number of the camera.
        """
        print("Not Implemented")

    def GetCCDWidth(self):
        """
        Returns the CCD width in pixels
        """
        print("Not Implemented")

    def GetCCDHeight(self):
        """
        Returns: the CCD height in pixels
        """
        print("Not Implemented")

    def stopAcq(self):
        """Stops the acquisition without closing the connection to the camera."""
        print("Not Implemented")

    def setBinning(self,xbin,ybin):
        """
        Sets the binning of the camera if supported. Has to check if binning in X/Y can be different or not, etc.

        :param xbin:
        :param ybin:
        :return:
        """
        print("Not Implemented")

    def stopCamera(self):
        """Stops the acquisition and closes the connection with the camera.
        """
        try:
            #Closing the camera
            print("Not Implemented")
        except:
            #Camera failed to close
            print("Not Implemented")
