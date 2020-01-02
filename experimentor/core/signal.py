import weakref
from time import sleep

import zmq

from experimentor.config import settings
from experimentor.core.subscriber import Subscriber
from experimentor.lib.log import get_logger

_signals = weakref.WeakSet()


logger = get_logger(__name__)


class Signal:
    """ Base signal which implements the common pattern for defining, emiting and connecting a signal
    """
    _name = None
    _owner = None

    def __init__(self):
        self.subscribers = {}
        self.pusher = None

    def emit(self, *args, **kwargs):
        if len(self.subscribers):
            logger.debug(f'Emitting signal {self}(args={args})(kwargs={kwargs}) to {len(self.subscribers)} subscribers')
            data = {}
            if args:
                data['args'] = args
            if kwargs:
                data['kwargs'] = kwargs

            self.pusher.send_string(self.topic, zmq.SNDMORE)
            self.pusher.send_pyobj(data)
            return
        logger.debug(f'Emitting {self} to 0 subscribers')

    def connect(self, func):
        """ Connects a signal to a given function. If it is the first connection which is made, a socket will be created
        to publish the data. This may be time consuming, sometimes when creating sockets it is necessary to wait for few
        seconds. It also starts a subscriber for the given function, which may add even more delay to the instantiation.
        """
        if not self.pusher:
            logger.debug(f'Pusher not yet initialized on {self}')
            context = zmq.Context()
            self.pusher = context.socket(zmq.PUSH)
            self.pusher.connect(f"tcp://127.0.0.1:{settings.PUBLISHER_PULL_PORT}")
            sleep(1)

        logger.debug(f'Connecting {func.__name__} to {self}')
        s = Subscriber(func, self.topic)
        s.start()
        self.subscribers.update({func.__name__: s})

    def disconnect(self, method):
        pass

    @property
    def topic(self):
        return f"{self._name}-{self._owner}"

    def __str__(self):
        return f"Signal {self._name} from {self._owner}"

    def __repr__(self):
        return f"Signal {self._name} from {self._owner}"
