import weakref
from multiprocessing.context import Process
from threading import Thread

from experimentor.lib.log import get_logger


class MetaProcess(type):
    """ Meta Class that should be shared by all processes in order to be sure they all switch off nicely when done.
    """
    def __init__(cls, name, bases, attrs):
        # Create class
        super(MetaProcess, cls).__init__(name, bases, attrs)

        # Initialize fresh instance storage
        cls._instances = weakref.WeakSet()

    def __call__(cls, *args, **kwargs):
        # Create instance (calls __init__ and __new__ methods)
        proc = super(MetaProcess, cls).__call__(*args, **kwargs)

        # Store weak reference to instance. WeakSet will automatically remove
        # references to objects that have been garbage collected
        cls._instances.add(proc)

        return proc

    def get_instances(cls, recursive=False):
        """Get all instances of this class in the registry. If recursive=True
        search subclasses recursively"""
        instances = list(cls._instances)
        if recursive:
            for Child in cls.__subclasses__():
                instances += Child.get_instances(recursive=recursive)

        # Remove duplicates from multiple inheritance.
        return list(set(instances))


class ExperimentorProcess(Process, metaclass=MetaProcess):
    def __init__(self, *args, **kwargs):
        super(ExperimentorProcess, self).__init__()
        self.logger = get_logger()


class ExperimentorThread(Thread, metaclass=MetaProcess):
    def __init__(self, *args, **kwargs):
        super(ExperimentorThread, self).__init__(args, kwargs)
        self.logger = get_logger()
