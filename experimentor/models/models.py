"""
MODELS
======
Models are a buffer between user interactions and real devices. Models should define at least some basic common
properties, for example how to read a value from a sensor and how to apply a value to an actuator.
Models can also take care of manipulating data, for example calculating an FFT and returning it to the user.
"""
import atexit
import multiprocessing as mp
import warnings
import weakref
from abc import abstractmethod

from experimentor.config import settings
from experimentor.core.exceptions import ModelDefinitionException
from experimentor.core.publisher import start_publisher
from experimentor.core.signal import Signal
from experimentor.lib.log import get_logger


logger = get_logger(__name__)


class MetaModel(type):
    """ Meta Model type which will be responsible for keeping track of all the created models in the program.
    This is very useful for things like automatically building a GUI, initializing/finishing all the devices, etc. and
    also to perform checks at the beginning of the runtime, by doing introspection on all the defined models, regardless
    of whether they are instantiated later on or no.

    One of the tasks is to generate a list of signals available in each model. Signals are specified as class attributes
    and therefore they can be accounted for before instantiating the class. Once the class is being instantiated, each
    object will re-instantiate the signals in order to keep its own copy, and establishing the proper owner of the
    signal.
    """

    def __init__(cls, name, bases, attrs):
        # Create class
        super(MetaModel, cls).__init__(name, bases, attrs)

        # Check whether the publisher exists or instantiate it and append it to the class
        # if not hasattr(settings, 'publisher'):
        #     logger.info("Publisher not yet initialized. Initializing it")
        #     start_publisher()

        if {'_signals', 'signals'} & set(attrs):
            raise ModelDefinitionException('Experiments should not define the _signals nor signals attribute themselves')

        cls._signals = {}
        for base in bases:
            if hasattr(base, '_signals'):
                cls._signals.update(base._signals)

        for attr, value in attrs.items():
            if isinstance(value, Signal):
                cls._signals[attr] = value
                value._name = attr

        if hasattr(cls, '__doc__') and cls.__doc__:
            cls.__doc__ += f"Available signals: {cls._signals}"
        else:
            cls.__doc__ = f"Available signals: {cls._signals}"

        # Initialize fresh instance storage
        cls._instances = weakref.WeakSet()
        cls._models = weakref.WeakSet()
        cls._models.add(cls)

    def __call__(cls, *args, **kwargs):
        # Create instance (calls __init__ and __new__ methods)
        inst = super(MetaModel, cls).__call__(*args, **kwargs)

        # Store weak reference to instance. WeakSet will automatically remove
        # references to objects that have been garbage collected
        cls._instances.add(inst)

        if hasattr(inst, 'signals'):
            warnings.warn('The model is defining its own signals. This is not expected behavior, beware!')
        else:
            inst.signals = {}

        for name, signal in inst._signals.items():
            sig = Signal()
            sig.set_owner(str(id(inst)))
            setattr(inst, name, sig)
            inst.signals[name] = sig

        return inst

    def get_instances(cls, recursive=False):
        """Get all instances of this class in the registry. If recursive=True
        search subclasses recursively"""
        instances = list(cls._instances)
        if recursive:
            for Child in cls.__subclasses__():
                instances += Child.get_instances(recursive=recursive)

        # Remove duplicates from multiple inheritance.
        return list(set(instances))

    def get_models(cls, recursive=False):
        """Gets all the models which share the MetaModel origin.
        """
        models = list(cls._models)
        if recursive:
            for child in cls.__subclasses__():
                models += child.get_models(recursive=recursive)
        return list(models)


class BaseModel(metaclass=MetaModel):
    """All models should inherit from this base model. It defines some basic methods and checks that prevent errors
    later at runtime.
    """
    def __init__(self):
        atexit.register(self.finalize)
        self._threads = []

    def clean_up_threads(self):
        """ Keep only the threads that are alive.
        """
        self._threads = [thread for thread in self._threads if thread[1].is_alive()]

    @classmethod
    def as_process(cls, *args, **kwargs):
        return ProxyObject(cls, *args, **kwargs)

    @abstractmethod
    def finalize(self):
        pass


class ProxyObject:
    def __init__(self, cls, *args, **kwargs):
        self.parent_pipe, child_pipe = mp.Pipe()
        if args:
            args = (cls, child_pipe, args)
        else:
            args = (cls, child_pipe)
        self.child_process = mp.Process(target=_create_process_loop, args=args, kwargs=kwargs)
        self.child_process.start()
        print(self.parent_pipe.recv())

        atexit.register(lambda: self.parent_pipe.send(None))


def _create_process_loop(cls, command_pipe, *args, **kwargs):
    if args:
        if kwargs:
            obj = cls(args, kwargs)
        else:
            obj = cls(kwargs)
    elif kwargs:
        obj = cls(kwargs)
    else:
        obj = cls()

    command_pipe.send('Instantiated')
    while True:
        try:
            cmd = command_pipe.recv()
        except EOFError:  # This implies the parent is dead; exit.
            return None
        if cmd is None: # This is how the parent signals us to exit.
            print('Exiting')
            return None
        attr_name, args, kwargs = cmd
        result = getattr(obj, attr_name)(*args, **kwargs)
        if callable(result):
            result = lambda: None  # Cheaper than sending a real callable
        command_pipe.send((result))




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


class ModelDevice(BaseModel, metaclass=MetaDevice):
    """ All models for devices should inherit from this class.
    """
    def __init__(self):
        super().__init__()
