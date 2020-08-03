"""
    Settings
    ========
    Every model has settings. These are values that are normally set only once, or only once per measurement. For example,
    the exposure time of a camera is normally set before acquiring a movie.

    Settings define two behaviors: When the user applies a value to a device, and when the the user wants to retrieve
    the value *from* the device. It is expected that settings do not change over time, and therefore, unless the user
    explicitly forces the update of a value, the setting is stored in a cache and always retrieved from there. This
    allows to access settings are often as needed, without choking the device.
"""
from experimentor.models.exceptions import ModelException


class Setting:
    """ Settings of models. It can be used as a decorator of methods in models. The settings will be stored in a
    dictionary owned by the model, and the values will be retrieved from there, unless explicitly told to update the
    value from the device.
    """
    def __init__(self, fget=None, fset=None, doc=None, **kwargs):
        self.fget = fget
        self.fset = fset
        self.doc = doc
        self.kwargs = kwargs

    def __set_name__(self, owner, name):
        # The following code takes care of making the settings available only to child classes but not to parents.
        settings = owner._settings
        if getattr(settings, 'settings_name', None) != object.__qualname__:
            settings = settings.__class__(**settings)
            setattr(settings, 'settings_name', object.__qualname__)
            owner._settings = settings

        owner._settings[name] = {'setting': self, 'value': None}
        self.name = name

    def __get__(self, instance, owner):
        self.instance = instance
        if instance._settings[self.name]['value'] is not None:
            return instance._settings[self.name]['value']
        if self.fget is None:
            raise ModelException(f'Setting {self.name} is unreadable')
        val = self.fget(instance)
        instance._settings[self.name]['value'] = val
        return val

    def __set__(self, instance, value):
        if self.fset is None:
            raise ModelException(f'Setting {self.name} is read-only')
        if value is None:
            instance._settings[self.name]['value'] = self.fget(instance)
        else:
            self.fset(instance, value)
            instance._settings[self.name]['value'] = self.fget(instance)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.doc, **self.kwargs)

    def update(self):
        val = self.fget(self.instance)
        return val


if __name__ == '__main__':
    from experimentor.models.models import BaseModel
    class Mod(BaseModel):
        def __init__(self):
            super().__init__()
            self._exp = 0

        @Setting
        def exposure_time(self):
            return self._exp

        @exposure_time.setter
        def exposure_time(self, val):
            self._exp = val

    mod = Mod()
    print(mod.exposure_time)
    mod.exposure_time = 2
    print(mod.exposure_time)
    # mod.exposure_time = None
    print(mod.exposure_time)