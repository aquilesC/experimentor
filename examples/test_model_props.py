from experimentor.models.devices.base_device import ModelDevice
from experimentor.models.model_properties import ModelProp


class TestModel(ModelDevice):
    def __init__(self):
        super().__init__()
        self._param = 0
        self.param = 1
        self.config.autolink()

    @ModelProp()
    def param(self):
        return self._param

    @param.setter
    def param(self, val):
        self._param = val


tm = TestModel()
print(tm._model_props)
tm._model_props['param'] = 100
print(tm.param)

print(tm.config._links)
tm.config.fetch_all()
print(tm.config['param'])
print(tm.config._links)
print(tm.config._links)
tm.param = 2
print(tm.config)
tm.config['param'] = 3
print(tm.config.to_update())
print(tm.config._links)
print(tm.config)
