"""
    Subscriber
    ==========
    Example script on how to run separate processes to process the data coming from a publisher like the one on
    ``publisher.py``. The first process just grabs the frame and puts it in a Queue. The Queue is then used by
    another process in order to analyse, process, save, etc. It has to be noted that on UNIX systems, getting
    from a queue with ``Queue.get()`` is particularly slow, much slower than serializing a numpy array with
    cPickle.

    .. Warning::
        This is work in process. On Windows, since processes are spawned, the subscriber would not work as expected.
        That is why we work with Threads instead.
"""
from multiprocessing import Process
from time import sleep

import numpy as np
import zmq

from experimentor.config import settings
from experimentor.core.meta import ExperimentorProcess
from experimentor.core.pusher import Pusher
from experimentor.lib.log import get_logger


class Subscriber(ExperimentorProcess):
    def __init__(self, func, topic, publish_topic=None, args=None, kwargs=None):
        super(Subscriber, self).__init__()
        self.func = func
        self.topic = topic
        self.publish_topic = publish_topic
        self.args = args
        self.kwargs = kwargs
        self.logger = get_logger()
        self.logger.info(f'Starting subscriber for {func.__name__} on topic {topic}')

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(f"tcp://localhost:{settings.PUBLISHER_PUBLISH_PORT}")
        if self.publish_topic:
            listener = Pusher()
        topic_filter = self.topic.encode('utf-8')
        socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
        self.logger.info(f'subscriber for {self.func.__name__} on topic {self.topic} ready')

        while not settings.GENERAL_STOP_EVENT.is_set():
            topic = socket.recv_string()
            self.logger.debug(f"Got data on topic {topic}")
            metadata = socket.recv_json(flags=0)
            if metadata.get('numpy', False):
                msg = socket.recv(flags=0, copy=True, track=False)
                buf = memoryview(msg)
                data = np.frombuffer(buf, dtype=metadata['dtype'])
                data = data.reshape(metadata['shape']).copy()
            else:
                data = socket.recv_pyobj()  # flags=0, copy=True, track=False)
            if isinstance(data, str):
                if data == settings.SUBSCRIBER_EXIT_KEYWORD:
                    self.logger.info(f'Stopping Subscriber {self}')
                    break
            ans = self.func(data)#, *self.args, **self.kwargs)
            if self.publish_topic:
                listener.publish(ans, self.publish_topic)

        sleep(1)  # Gives enough time for the publishers to finish sending data before closing the socket
        socket.close()

    def stop(self):
        with Pusher() as pusher:
            pusher.publish(settings.SUBSCRIBER_EXIT_KEYWORD)
        self.join()

    def __str__(self):
        return f"Subscriber {self.func.__name__}"

    def __repr__(self):
        return f"<Subscriber {self.func.__name__}>"
