"""
Meta Models
===========

:license: MIT, see LICENSE for more details
:copyright: 2020 Aquiles Carattino
"""
import weakref

from experimentor.core.exceptions import ModelDefinitionException
from experimentor.core.signal import Signal


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

        return inst

    def get_instances(cls, recursive=False):
        """Get all instances of this class in the registry.

        Parameters
        ----------
        recursive: bool
            Search for instances recursively through inherited objects
        """
        instances = list(cls._instances)
        if recursive:
            for Child in cls.__subclasses__():
                instances += Child.get_instances(recursive=recursive)

        # Remove duplicates from multiple inheritance.
        return list(set(instances))

    def get_models(cls, recursive=False):
        """Gets all the models which share the MetaModel origin.

        Parameters
        ----------
        recursive: bool
            Search recurisvely in sub classes of the model
        """
        models = list(cls._models)
        if recursive:
            for child in cls.__subclasses__():
                models += child.get_models(recursive=recursive)
        return list(models)