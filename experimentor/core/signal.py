from experimentor.lib.log import get_logger


logger = get_logger(__name__)


class Signal:
    """ Base signal which implements the common pattern for defining, emitting and connecting a signal
    """
    def __init__(self):
        self.name = None

    def __set_name__(self, owner, name):
        model_signals = getattr(owner, '_signals')

        if getattr(model_signals, 'model_name', None) != object.__qualname__:
            model_signals = model_signals.__class__(*model_signals)
            setattr(model_signals, 'model_name', object.__qualname__)
            setattr(owner, '_signals', model_signals)

        model_signals[name] = self

        self.name = name
        self.owner = str(owner)

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def emit(self, payload=None, **kwargs):
        """ Emitting a signal relies on the owner's publisher or whatever method the owner specifies for broadcasting.
        In principle this allows for some flexibility in case owners use different ways of broadcasting information.
        For example, the owner could be a QObject and it could use the internals of Qt to emitting signals.

        """
        logger.debug(f'Emitting {self.name} from {self.owner}')
        self.instance.emit(self.name, payload, **kwargs)

    @property
    def url(self):
        return f"{self.instance.get_publisher_url()}:{self.instance.get_publisher_port()}"

    def __str__(self):
        return f"Signal {self.name} from {self.owner}"

    def __repr__(self):
        return f"Signal {self.name} from {self.owner}"