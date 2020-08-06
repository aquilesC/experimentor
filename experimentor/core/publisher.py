# -*- coding: utf-8 -*-
"""
Publisher
=========

Publishers are responsible for broadcasting the message over the ZMQ PUB/SUB architecture. The publisher runs
continuously on a separated process and grabs elements from a queue, which in turn are sent through a socket to any
other processes listening.

.. TODO:: In the current implementation, data is serialized for being added to a Queue, then deserialized by the
    publisher and serialized again to be sent. These three steps could be simplify into one if, for example, one assumes
    that objects where pickled. There is also a possibility of assuming numpy arrays and using a zero-copy strategy.

:copyright:  Aquiles Carattino
:license: MIT, see LICENSE for more details
"""
import atexit
from time import sleep

import zmq

from experimentor.config import settings
from experimentor.core.pusher import Pusher
from experimentor.lib.log import get_logger
from .meta import MetaProcess, ExperimentorProcess

logger = get_logger(name=__name__)


class Publisher(ExperimentorProcess, metaclass=MetaProcess):
    """ Publisher class in which the queue for publishing messages is defined and also a separated process is started.
    It is important to have a new process, since the serialization/deserialization of messages from the QUEUE may be
    a bottleneck for performance.
    """

    def __init__(self, event, name=None):
        super(Publisher, self).__init__(name=name or 'Publisher')
        self._event = event  # This event is used to stop the process
        self.running = False
        atexit.register(self.stop)

    def run(self):
        """ Start a new process that will be responsible for broadcasting the messages.

            .. TODO:: Find a way to start the publisher on a different port if the one specified is in use.
        """
        self.running = True
        logger.info('Publisher initializing')
        context = zmq.Context()
        publisher = context.socket(zmq.PUB)
        try:
            publisher.bind(f"tcp://*:{settings.PUBLISHER_PUBLISH_PORT}")
        except zmq.ZMQError:
            logger.error('Por already in use. Trying to close and reconnect')
            temp = context.socket(zmq.PUSH)
            temp.connect(f"tcp://127.0.0.1:{settings.PUBLISHER_PULL_PORT}")
            temp.send_string("", zmq.SNDMORE)
            temp.send_pyobj(settings.PUBLISHER_EXIT_KEYWORD)
            sleep(1)
            logger.info('Retrying to open the publisher')
            try:
                publisher.bind(f"tcp://*:{settings.PUBLISHER_PUBLISH_PORT}")
            except zmq.ZMQError:
                raise

        listener = context.socket(zmq.PULL)
        listener.bind(f"tcp://127.0.0.1:{settings.PUBLISHER_PULL_PORT}")

        sleep(2)  # To give time to binding to the given port
        i = 0
        logger.info('Publisher ready to handle events')
        while not self._event.is_set():
            topic = listener.recv_string()
            logger.debug(f"Got data on topic {topic}")
            metadata = listener.recv_json(flags=0)
            publisher.send_string(topic, zmq.SNDMORE)
            publisher.send_json(metadata, 0 | zmq.SNDMORE)
            if metadata.get('numpy', False):
                data = listener.recv(flags=0, copy=True, track=False)
                publisher.send(data, 0, copy=True, track=False)
            else:
                data = listener.recv_pyobj()
                publisher.send_pyobj(data)
            i += 1
            logger.debug(data)

            if topic == "":
                logger.info('Got Broad Topic')
                if isinstance(data, str) and data == settings.PUBLISHER_EXIT_KEYWORD:
                    logger.debug('Stopping the Publisiher')
                    self._event.set()
        logger.info('Publisher Stopped')
        self.running = False

    def stop(self):
        with Pusher() as pusher:
            pusher.publish(settings.PUBLISHER_EXIT_KEYWORD)
        self.join()


def start_publisher():
    """Wrapper function to start the publisher. It takes care of checking that there is only one publisher running by
    storing it in the settings.

    .. TODO:: Find a good way of starting a publisher once per measurement cycle.
    """
    if hasattr(settings, 'publisher'):
        logger.warning('Publisher already defined')
        if settings.publisher.is_alive():
            logger.warning('Publisher is alive, but trying to start another instance')
            return
        settings.publisher.start()
    settings.publisher = Publisher(settings.GENERAL_STOP_EVENT)
    settings.publisher.start()
    settings.PUBLISHER_READY = True