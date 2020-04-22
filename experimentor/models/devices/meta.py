import weakref

from experimentor.models.meta import MetaModel


class MetaDevice(MetaModel):
    """
    This is a Meta Class that should be used only by devices and not by the experiment itself. It is only to give
    more granularity to the program when wanting to perform operations on all the devices or on different possible
    measurements.
    """
    def __init__(cls, name, bases, attrs):
        super(MetaDevice, cls).__init__(name, bases, attrs)
        cls._devices_class = weakref.WeakSet()
        cls._devices_class.add(cls)
        cls._devices = weakref.WeakSet()

    def __call__(cls, *args, **kwargs):
        inst = super(MetaDevice, cls).__call__(*args, **kwargs)
        cls._devices.add(inst)
        return inst
