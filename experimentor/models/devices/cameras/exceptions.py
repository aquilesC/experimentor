from experimentor.models.devices.exceptions import DeviceException


class CameraException(DeviceException):
    pass


class CameraNotFound(CameraException):
    pass