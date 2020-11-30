"""
    Features
    ========
    Features in a model are those parameters that can be read, set, or both. They were modeled after Lantz Feat objects,
    and the idea is that they can encapsulate common patterns in device control. They are similar to :mod:`~Settings` in
    behavior, except for the absence of a cache. Features do communicate with the device when reading a value.

    For example, a feature could be the value of an analog input on a DAQ, or the temperature of a camera. They are
    meant to be part of a measurement, their values can change in loops in order to make a scan. Features can be used
    as decorators in pretty much the same way @propery can be used. The only difference is that they register
    themselves in the models properties object, so it is possible to update values either by submitting a value
    directly to the Feature or by sending a dictionary to the properties and updating all at once.

    It is possible to mark a feature as a setting. In this case, the value will not be read from the device, but it will
    be cached. In case it is needed to refresh a value from the device, it is possible to use a specific argument, such
    as ``None``. For example::

        @Feature(setting=True, force_update_arg=0)
        def exposure(self):
            self.driver.get_exposure()

        @exposure.setter
        def exposure(self, exposure_time):
            self.driver.set_exposure(exposure_time)

    .. TODO:: It is possible to define complex behavior such as unit conversion, limit checking, etc. We should narrow
        down what is appropriate for a model and what should go into the Controller.

    .. TODO:: A useful pattern is to catch the exception raised by the controllers if a value is out of range, or with
        the wrong units.

    :license: MIT, see LICENSE for more details
    :copyright: 2020 Aquiles Carattino
"""


class Feature:
    """ Properties that belong to models. It makes easier the setting and getting of attributes, while at the same
    time it keeps track of the properties of each model. A Feature is, fundamentally, a descriptor, that extends some
    functionality by accepting keyword arguments when defining.

    .. todo:: There is a lot of functionality that can be implemented, but that hasn't yet, such as checking limits,
        unit conversion, etc.

    Attributes
    ----------
    name : str
        The name of the feature, it must be unique since it will be used as a key in a dictionary.
    kwargs : dict
        If the feature is initialized with arguments, they will be stored here. Only keyword arguments are allowed.
    """

    name = ''
    kwargs = None

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self.kwargs = kwargs
        self.owner = None

        self.is_setting = self.kwargs.get('setting', False)
        self.force_update = self.kwargs.get('force_update_arg', None)
        self.value = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")

        if self.is_setting and self.value != self.force_update:
            return self.value

        val = self.fget(instance)
        instance.config.upgrade({self.name: val}, force=True)
        return val

    def __set__(self, instance, value):
        if self.fset is None and not self.is_setting:
            raise AttributeError("can't set attribute")
        if self.is_setting:
            if self.force_update == value:
                value = self.fget(instance)
            else:
                raise AttributeError(f"Can't set a setting, and {value} is not the value to trigger a reset. Should be {self.force_update}")
        else:
            self.fset(instance, value)
        self.value = value
        instance.config.upgrade({self.name: value}, force=True)

    def __set_name__(self, owner, name):
        # The following code is to work around inheritance in only one direction. This means that only child classes
        # should inherit properties of their parents, but not the other way around.
        if self.is_setting:
            model_props_var = '_settings'
        else:
            model_props_var = '_features'

        model_props = getattr(owner, model_props_var)

        if getattr(model_props, 'model_name', None) != object.__qualname__:
            # If the name of the class is different from the name registered as a property, we must create a new
            # instance, using the information already available

            model_props = model_props.__class__(**model_props)
            setattr(model_props, 'model_name', object.__qualname__)
            setattr(owner, model_props_var, model_props)

        model_props[name] = self

    def __call__(self, func):
        if self.fget is None:
            return self.getter(func)
        return self.setter(func)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__, **self.kwargs)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__, **self.kwargs)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__, **self.kwargs)

