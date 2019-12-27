import weakref

from experimentor.models.listener import Listener

_signals = weakref.WeakSet()


class Signal:
    """ Base signal which implements the common pattern for defining, emiting and connecting a signal
    """
    _name = None
    _owner = None

    def __init__(self):
        self.listener = Listener()

    def __call__(self, *args, **kwargs):
        print(args, kwargs)

    def emit(self, data=None):
        self.listener.publish(data, topic=self.topic)

    def connect(self, method):
        pass

    def disconnect(self, method):
        pass

    @property
    def topic(self):
        return f"{self._name}-{self._owner}"

    def __str__(self):
        return f"Signal {self._name} from {self._owner}"

    def __repr__(self):
        return f"Signal {self._name} from {self._owner}"
