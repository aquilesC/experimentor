from experimentor.models.models import BaseModel, MetaDevice
from experimentor.models.properties import Properties


class ModelDevice(BaseModel, metaclass=MetaDevice):
    """ All models for devices should inherit from this class.
    """
    def __init__(self):
        super().__init__()
        self.config = Properties(self)

    def __str__(self):
        return f"Model {id(self)}"
