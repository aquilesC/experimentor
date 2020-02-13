from experimentor.models.models import BaseModel


class MyModel(BaseModel):
    def __init__(self):
        super().__init__()

    def finalize(self):
        pass

    def initialize(self):
        pass