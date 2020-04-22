"""
MODELS
======
Models are a buffer between user interactions and real devices. Models should define at least some basic common
properties, for example how to read a value from a sensor and how to apply a value to an actuator.
Models can also take care of manipulating data, for example calculating an FFT and returning it to the user.
"""
import atexit
import multiprocessing as mp
from abc import abstractmethod

from experimentor.models.meta import MetaModel


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

    @property
    def subscribers(self):
        return [sub for sub in self._subscribers if sub.is_alive()]

    @classmethod
    def as_process(cls, *args, **kwargs):
        return ProxyObject(cls, *args, **kwargs)

    @abstractmethod
    def initialize(self):
        pass

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
