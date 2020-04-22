from experimentor.core.pusher import Pusher
from experimentor.core.subscriber import Subscriber
from experimentor.lib.log import get_logger


logger = get_logger(__name__)


class Signal:
    instance = None
    owner = None
    name = None
    """ Base signal which implements the common pattern for defining, emiting and connecting a signal
    """
    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner
        self.instace = None
        self.pusher = None
        self.subscribers = []
        if owner is not None:
            if not hasattr(owner, '_signals'):
                owner._signals = {self.name: self}
            else:
                owner._signals.update({self.name: self})

    def __get__(self, instance, owner):
        if instance is None:
            return self
        self.instace = instance
        return instance._signals[self.name]

    def __set__(self, instance, value):
        raise AttributeError('Signals can\'t be overwritten')

    def emit(self, *args, **kwargs):
        if len(self.subscribers):
            logger.debug(f'Emitting {self}(args={args})(kwargs={kwargs}) to {len(self.subscribers)} subscribers')
            data = {}
            if args:
                data['args'] = args
            if kwargs:
                data['kwargs'] = kwargs

            self.pusher.publish(data, self.topic)

            return
        logger.debug(f'Emitting {self} to {len(self.subscribers)} subscribers')

    def connect(self, func):
        """ Connects a signal to a given function. If it is the first connection which is made, a socket will be created
        to publish the data. This may be time consuming, sometimes when creating sockets it is necessary to wait for few
        seconds. It also starts a subscriber for the given function, which may add even more delay to the instantiation.
        """
        if not self.pusher:
            logger.debug(f'Pusher not yet initialized on {self}')
            self.pusher = Pusher()

        logger.debug(f'Connecting {func.__name__} to {self}')
        s = Subscriber(func, self.topic)
        s.start()
        self.instace._subscribers.append(s)
        self.subscribers.append(func.__name__)

    def disconnect(self, method):
        pass

    @property
    def topic(self):
        if self.instace:
            return f"{self.name}-{id(self.instance)}"
        if self.owner:
            return f"{self.name}-{id(self.owner)}"
        return f"{self.name}-0"

    def __str__(self):
        return f"Signal {self.name} from {self.owner}"

    def __repr__(self):
        return f"Signal {self.name} from {self.owner}"

    def __call__(self, *args, **kwargs):
        print(self.instace)

