"""
    Subscriber
    ==========
    Example script on how to run separate processes to process the data coming from a publisher like the one on
    ``publisher.py``. The first process just grabs the frame and puts it in a Queue. The Queue is then used by
    another process in order to analyse, process, save, etc. It has to be noted that on UNIX systems, getting
    from a queue with ``Queue.get()`` is particularly slow, much slower than serializing a numpy array with
    cPickle.
"""
from threading import Thread
from time import sleep

import numpy as np
import zmq

from experimentor.config import settings
from experimentor.core.meta import MetaProcess
from experimentor.core.pusher import Pusher
from experimentor.lib.log import get_logger

logger = get_logger(__name__)


class Subscriber(Thread, metaclass=MetaProcess):
    def __init__(self, func, url, topic):
        super(Subscriber, self).__init__()
        logger.info(f'Starting subscriber for {func.__name__} on topic {topic}')
        self.func = func
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(url)
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")  # topic.encode('utf-8'))
        self.start()

    def run(self):
        while not settings.GENERAL_STOP_EVENT.is_set():
            event = self.socket.poll(0)
            if not event:
                sleep(.005)
                continue
            topic = self.socket.recv_string()
            logger.debug(f"Got data on topic {topic}")
            metadata = self.socket.recv_json(flags=0)
            if metadata.get('numpy', False):
                msg = self.socket.recv(flags=0, copy=True, track=False)
                buf = memoryview(msg)
                data = np.frombuffer(buf, dtype=metadata['dtype'])
                data = data.reshape(metadata['shape']).copy()
            else:
                data = self.socket.recv_pyobj()  # flags=0, copy=True, track=False)
            if isinstance(data, str):
                if data == settings.SUBSCRIBER_EXIT_KEYWORD:
                    logger.info(f'Stopping Subscriber {self}')
                    break
            self.func(data)#, *self.args, **self.kwargs)
        sleep(1)  # Gives enough time for the publishers to finish sending data before closing the socket
        self.socket.close()

    def stop(self):
        with Pusher() as pusher:
            pusher.publish(settings.SUBSCRIBER_EXIT_KEYWORD, self.topic)
        self.join()

    def __str__(self):
        return f"Subscriber {self.func.__name__}"

    def __repr__(self):
        return f"<Subscriber {self.func.__name__}>"
