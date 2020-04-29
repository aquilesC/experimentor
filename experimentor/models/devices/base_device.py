from experimentor.models.devices.meta import MetaDevice
from experimentor.models.models import BaseModel
from experimentor.models.properties import Properties


class ModelDevice(BaseModel, metaclass=MetaDevice):
    """ All models for devices should inherit from this class. """

    _driver = None

    def __init__(self):
        super().__init__()
        self.config = Properties(self)
        # self.config.autolink()

    def __str__(self):
        return f"Model {id(self)}"
