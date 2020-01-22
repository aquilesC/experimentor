# -*- coding: utf-8 -*-
"""
    base_experiment.py
    ==================
    Base class for the experiments. ``BaseExperiment`` defines the common patterns that every experiment should have.
    Importantly, it starts an independent process called publisher, that will be responsible for broadcasting messages
    that are appended to a queue. The messages rely on the pyZMQ library and should be tested further in order to
    assess their limitations. The general pattern is that of the PUB/SUB, with one publisher and several subscribers.

    The messages should include a *topic* and data. For this, the elements in the queue should be dictionaries with two
    keywords: **data** and **topic**. ``data['data']`` will be serialized through the use of cPickle, and is handled
    automatically by pyZQM through the use of ``send_pyobj``. The subscribers should be aware of this and use either
    unpickle or ``recv_pyobj``.

    In order to stop the publisher process, the string ``'stop'`` should be placed in ``data['data']``. The message
    will be broadcast and can be used to stop other processes, such as subscribers.

    .. TODO:: Check whether the serialization of objects with cPickle may be a bottleneck for performance.

    :license: GPLv3, see LICENSE for more details
"""
import weakref
from multiprocessing import Process, Event
from time import sleep

import yaml
import zmq

from experimentor.core.exceptions import ExperimentDefinitionException
from experimentor.core.signal import Signal
from experimentor.models.decorators import not_implemented, make_async_thread
from experimentor.lib.log import get_logger
from experimentor.models.listener import Listener
from experimentor.core.publisher import Publisher
from experimentor.core.subscriber import Subscriber
from experimentor.config import settings
from experimentor.models.models import MetaModel

_experiments = weakref.WeakSet()  # Stores all the defined experiments
logger = get_logger(__name__)


class MetaExperiment(MetaModel):
    """ Meta Model type which will be responsible for keeping track of all the created experiments. It will also be
    responsible for registering the publisher, in order to have only one throughout the program and accessible from
    other parts of the program. This meta class may be overkill, since in principle every program will be only one
    experiment, but this is left as an effort to be future-proof.

    .. note:: Defining meta classes may generate a feeling of obscurantism in the code. It may be wise to remove it and
        find a simpler/straightforward approach.

    """
    def __init__(cls, name, bases, attrs):
        # Create class
        super(MetaExperiment, cls).__init__(name, bases, attrs)

        if not attrs.get("_abstract", False):
            _experiments.add(cls)

    def __call__(cls, *args, **kwargs):
        # Create instance (calls __init__ and __new__ methods)
        inst = super(MetaExperiment, cls).__call__(*args, **kwargs)

        # Check whether the publisher exists or instantiate it and append it to the class
        if not hasattr(settings, 'publisher'):
            logger.info("Publisher not yet initialized. Initializing it")
            publisher = Publisher(settings.GENERAL_STOP_EVENT)
            publisher.start()
            settings.publisher = publisher
        else:
            publisher = settings.publisher

        inst.publisher = publisher

        # Store weak reference to instance. WeakSet will automatically remove
        # references to objects that have been garbage collected
        cls._instances.add(inst)

        return inst

    def _get_instances(cls, recursive=False):
        """Get all instances of this class in the registry. If recursive=True
        search subclasses recursively"""
        instances = list(cls._instances)
        if recursive:
            for Child in cls.__subclasses__():
                instances += Child._get_instances(recursive=recursive)

        # Remove duplicates from multiple inheritance.
        return list(set(instances))


class BaseExperiment(metaclass=MetaExperiment):
    _abstract = True


class Experiment(BaseExperiment):
    """ Base class to define experiments. Should keep track of the basic methods needed regardless of the experiment
    to be performed. For instance, a way to start and a way to finalize a measurement.
    """
    _abstract = True
    start = Signal()

    def __init__(self, filename=None):
        self.config = {}  # Dictionary storing the configuration of the experiment
        self.logger = get_logger(name=__name__)
        self._threads = []
        self.publisher = None
        self.listener = Listener()

        self._connections = []
        self.subscriber_events = []
        self.initialize_threads = []  # Threads to initialize several devices at the same time
        if filename:
            self.load_configuration(filename)

    def stop_publisher(self):
        """ Puts the proper data to the queue in order to stop the running publisher process
        """
        if not self.publisher:
            self.logger.info('Publisher never started, nothing to do here')
            return

        self.logger.info('Stopping the publisher')
        self.publisher.stop()
        self.stop_subscribers()

    def stop_subscribers(self):
        """ Puts the proper data into every alive subscriber in order to stop it.
        """
        self.logger.info('Stopping the subscribers')
        for event in self.subscriber_events:
            event.set()

        for connection in self._connections:
            if connection['process'].is_alive():
                self.logger.info('Stopping {}'.format(connection['method']))
                connection['event'].set()

    def connect(self, method, topic, *args, **kwargs):
        """ Async method that connects the running publisher to the given method on a specific topic.

        :param method: method that will be connected on a given topic
        :param str topic: the topic that will be used by the subscriber to discriminate what information to collect.
        :param args: extra arguments will be passed to the subscriber, which in turn will pass them to the function
        :param kwargs: extra keyword arguments will be passed to the subscriber, which in turn will pass them to the function
        """
        event = Event()
        self.logger.debug('Arguments: {}'.format(args))
        arguments = [method, topic, event]
        for arg in args:
            arguments.append(arg)

        self.logger.info('Connecting {} on topic {}'.format(method.__name__, topic))
        self.logger.debug('Arguments: {}'.format(args))
        self.logger.debug('KWarguments: {}'.format(kwargs))
        self._connections.append({
            'method':method.__name__,
            'topic': topic,
            'process': Process(target=Subscriber, args=arguments, kwargs=kwargs),
            'event': event,
        })
        self._connections[-1]['process'].start()

    def load_configuration(self, filename):
        """ Loads the configuration file in YAML format.

        :param str filename: full path to where the configuration file is located.
        :raises FileNotFoundError: if the file does not exist.
        """
        self.logger.info('Loading configuration file {}'.format(filename))
        try:
            with open(filename, 'r') as f:
                self.config = yaml.load(f, Loader=yaml.SafeLoader)
                self.logger.debug('Config loaded')
                self.logger.debug(self.config)
        except FileNotFoundError:
            self.logger.error('The specified file {} could not be found'.format(filename))
            raise
        except Exception as e:
            self.logger.exception('Unhandled exception')
            raise

    @property
    def initializing(self):
        """ Checks whether the devices are initializing or not. It does not distinguish between initialization not
        triggered yet and initialization finalized.
        """
        return any([t.is_alive() for t in self.initialize_threads])

    def clear_threads(self):
        """ Keep only the threads that are alive.
        """
        self._threads = [thread for thread in self._threads if thread[1].is_alive()]

    @property
    def num_threads(self):
        return len(self._threads)

    @property
    def connections(self):
        return [conn for conn in self._connections if conn['process'].is_alive()]

    @property
    def alive_threads(self):
        alive_threads = 0
        for thread in self._threads:
            if thread[1].is_alive():
                alive_threads += 1
        return alive_threads

    @property
    def list_alive_threads(self):
        alive_threads = []
        for thread in self._threads:
            if thread[1].is_alive():
                alive_threads.append(thread)
        return alive_threads

    @not_implemented
    def set_up(self):
        """ Needs to be overridden by child classes.
        """
        pass

    def finalize(self):
        """ Needs to be overridden by child classes.
        """
        for subscriber in Subscriber._get_instances():
            self.listener.publish(settings.SUBSCRIBER_EXIT_KEYWORD, subscriber.topic)
            while subscriber.is_alive():
                sleep(0.001)
        if self.listener:
            self.listener.publish(settings.PUBLISHER_EXIT_KEYWORD, "")
            self.listener.finish()
        else:
            self.logger.info('Listener not started and already finalizing. Nothing to do')

        if self.publisher:
            self.publisher.stop()
        else:
            self.logger.info('Publisher not started and already finalizing. Nothing to do here')

    def update_config(self, **kwargs):
        self.logger.info('Updating config')
        self.logger.debug('Config params: {}'.format(kwargs))
        self.config.update(**kwargs)

    def __enter__(self):
        self.set_up()
        return self

    def __del__(self):
        self.finalize()

    def __exit__(self, *args):
        self.logger.info("Exiting the experiment")
        self.finalize()

        self.logger.debug('Number of open connections: {}'.format(len(self.connections)))
        for event in self.subscriber_events:
            event.set()

        for conn in self.connections:
            self.logger.debug('Waiting for {} to finish'.format(conn['method']))
            conn['process'].join()

        self.logger.info('Finished the base experiment')

        self.publisher.stop()

    @make_async_thread
    def connect(self, method, topic):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(f"tcp://localhost:{settings.PUBLISHER_PUBLISH_PORT}")
        sleep(1)
        topic_filter = topic.encode('utf-8')
        socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
        while not settings.GENERAL_STOP_EVENT.is_set():
            topic = socket.recv_string()
            data = socket.recv_pyobj()  # flags=0, copy=True, track=False)
            if isinstance(data, str):
                if data == settings.SUBSCRIBER_EXIT_KEYWORD:
                    self.logger.info(f'Stopping Subscriber {self}')
                    break
            method(data)

    def __repr__(self):
        return f"Experiment {id(self)}"