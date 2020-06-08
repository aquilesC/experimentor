from experimentor.models.devices.exceptions import DeviceException


class CameraException(DeviceException):
    pass


class WrongCameraState(CameraException):
    pass


class CameraNotFound(CameraException):
    pass


class CameraTimeout(CameraException):
    pass