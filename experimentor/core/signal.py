import weakref

from experimentor.core import listener
from experimentor.core.subscriber import Subscriber

_signals = weakref.WeakSet()


class Signal:
    """ Base signal which implements the common pattern for defining, emiting and connecting a signal
    """
    _name = None
    _owner = None

    def __init__(self):
        self.listener = listener
        self.subscribers = {}

    def emit(self, *args, **kwargs):
        data = {}
        if args:
            data['args'] = args
        if kwargs:
            data['kwargs'] = kwargs
        self.listener.publish(data, topic=self.topic)

    def connect(self, func):
        s = Subscriber(func, self.topic)
        s.start()
        self.subscribers[func.__name__] = s

    def disconnect(self, method):
        pass

    @property
    def topic(self):
        return f"{self._name}-{self._owner}"

    def __str__(self):
        return f"Signal {self._name} from {self._owner}"

    def __repr__(self):
        return f"Signal {self._name} from {self._owner}"
