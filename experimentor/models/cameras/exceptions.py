from experimentor.models.exceptions import ModelException


class DeviceModelException(ModelException):
    pass


class CameraException(DeviceModelException):
    pass


class CameraNotFound(DeviceModelException):
    pass


class WrongCameraState(DeviceModelException):
    pass


class CameraTimeout(DeviceModelException):
    pass
