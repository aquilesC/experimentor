"""
MODELS
======
Models are a buffer between user interactions and real devices. Models should define at least some basic common
properties, for example how to read a value from a sensor and how to apply a value to an actuator.
Models can also take care of manipulating data, for example calculating an FFT and returning it to the user.
"""
import atexit
import multiprocessing as mp
import time
from abc import abstractmethod
import numpy as np

import zmq

from experimentor.models.meta import MetaModel


class ExpDict(dict):
    pass


class ExpList(list):
    lock = mp.Lock()


class BaseModel(metaclass=MetaModel):
    """All models should inherit from this base model. It defines some basic methods and checks that prevent errors
    later at runtime.

    Attributes
    ----------
    _features : ExpDict
        Dictionary-like object to store the properties of the model
    _actions: ExpList
        List-like object to store the available actions. It also stores a lock to prevent multiple actions to be
        triggered at the same time
    _settings : ExpDict
        Dictionary-like object where the settings are stored. This dictionary is also used to retrieve the latest known
        value of the setting.
    """
    _features = ExpDict()
    _actions = ExpList()
    _settings = ExpDict()
    _signals = ExpDict()
    _subscribers = ExpDict()

    def __init__(self):
        atexit.register(self.finalize)
        self._threads = []
        self._ctx = self.create_context()
        self._publisher = self.create_publisher()

    def create_context(self):
        return zmq.Context()

    def get_context(self):
        return self._ctx

    def create_publisher(self):
        ctx = self.get_context()
        publisher = ctx.socket(zmq.PUB)
        publisher.bind('tcp://*:*')
        time.sleep(2)
        return publisher

    def get_publisher(self):
        return self._publisher

    def get_publisher_url(self):
        return 'tcp://localhost'

    def get_publisher_port(self):
        url = self.get_publisher().getsockopt(zmq.LAST_ENDPOINT).decode()
        return url.rsplit(":")[-1]

    def emit(self, signal_name, payload, **kwargs):
        """ Emits a signal using the publisher bound to the model. It uses the method :func:`BaseModel.get_publisher` to
        get the publisher to use. You can override that method in order to use a different publisher (for example, an
        experiment-based publisher instead of a model-based one.

        Notes
        -----
            If subscribers are too slow, a queue will build up on the publisher, which may lead to the model itself
            crashing. It is important to be sure subscribers can keep up.

        Parameters
        ----------
        signal_name : str
            The name of the signal is used as a topic for the publisher. Remember that in PyZMQ, topics are filtered on
            the subscriber side, therefore everything is always broadcasted broadly, which can be a bottleneck for
            performance in case there are many subscribers.
        payload
            It will be sent by the publisher. In case it is a ``numpy`` array, it will use a zero-copy strategy. For the
            rest, it will send using ``send_pyobj``, which serializes the payload using pickle. This can be a *slow*
            process for complex objects.
        kwargs
            Optional keyword arguments to make the method future-proof. Rigth now, the only supported keyword argument
            is ``meta``, which will append to the current meta_data being broadcast. For numpy arrays, metadata is a
            dictionary with the following keys: ``numpy``, ``dtype``, ``shape``. For non-numpy objects, the only key is
            ``numpy``. The submitted metadata is appended to the internal metadata, therefore be careful not to
            overwrite its keys unless you know what you are doing.
        """
        publisher = self.get_publisher()
        publisher.send_string(signal_name, zmq.SNDMORE)
        if 'meta' in kwargs:
            extra_meta = kwargs.get('meta')
        else:
            extra_meta = None

        meta_data = dict(numpy=False)
        if isinstance(payload, np.ndarray):
            meta_data = dict(
                numpy=True,
                dtype=str(payload.dtype),
                shape=payload.shape,
            )
            if extra_meta is not None:
                meta_data.update(extra_meta)
            publisher.send_json(meta_data, 0 | zmq.SNDMORE)
            publisher.send(payload, 0, copy=True, track=False)
        else:
            if extra_meta is not None:
                meta_data.update(extra_meta)
            publisher.send_json(meta_data, 0 | zmq.SNDMORE)
            publisher.send_pyobj(payload)

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

    def finalize(self):
        self._publisher.close()


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

        # atexit.register(lambda: self.parent_pipe.send(None))


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
            break
        if cmd is None: # This is how the parent signals us to exit.
            print('Exiting')
            break
        attr_name, args, kwargs = cmd
        result = getattr(obj, attr_name)(*args, **kwargs)
        if callable(result):
            result = lambda: None  # Cheaper than sending a real callable
        command_pipe.send((result))
