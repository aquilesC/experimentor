"""
MODELS
======
Models are a buffer between user interactions and real devices. Models should define at least some basic common
properties, for example how to read a value from a sensor and how to apply a value to an actuator.
Models can also take care of manipulating data, for example calculating an FFT and returning it to the user.
"""
import weakref
from experimentor.core.exceptions import ModelDefinitionException
from experimentor.core.signal import Signal


class MetaModel(type):
    """ Meta Model type which will be responsible for keeping track of all the created models in the program.
    This is very useful for things like automatically building a GUI, initializing/finishing all the devices, etc.
    """
    def __init__(cls, name, bases, attrs):
        # Create class
        super(MetaModel, cls).__init__(name, bases, attrs)

        if '_signals' in attrs:
            raise ModelDefinitionException('Experiments should not define the _signals attribute themselves')

        cls._signals = {}
        for base in bases:
            if hasattr(base, '_signals'):
                cls._signals.update(base._signals)

        for attr, value in attrs.items():
            if isinstance(value, Signal):
                cls._signals[attr] = value
                value._name = attr

        if cls.__doc__:
            cls.__doc__ += f"Available signals: {cls._signals}"
        else:
            cls.__doc__ = f"Available signals: {cls._signals}"

        # Initialize fresh instance storage
        cls._instances = weakref.WeakSet()

    def __call__(cls, *args, **kwargs):
        # Create instance (calls __init__ and __new__ methods)
        inst = super(MetaModel, cls).__call__(*args, **kwargs)

        # Store weak reference to instance. WeakSet will automatically remove
        # references to objects that have been garbage collected
        cls._instances.add(inst)

        for name, signal in inst._signals.items():
            signal._owner = id(inst)

        return inst

    def _get_instances(cls, recursive=False):
        """Get all instances of this class in the registry. If recursive=True
        search subclasses recursively"""
        instances = list(cls._instances)
        if recursive:
            for Child in cls.__subclasses__():
                instances += Child._get_instances(recursive=recursive)

        # Remove duplicates from multiple inheritance.
        return list(set(instances))


class BaseModel(metaclass=MetaModel):
    _config = dict()
