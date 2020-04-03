"""
    Pusher
    ======

    .. versionadded:: 0.2.0

    Half the ZMQ implementation is abut broadcasting information from a publisher to different subscribers. However, the
    other half is giving information to the publisher to broadcast. We are doing this with a PUSH/PULL pattern. The
    pusher is therefore able to send information to the Publisher to then broadcast. There can be many instances of
    pushers, but only one publisher. In other words, this is a fan-in type of architecture.
"""
import atexit
from threading import RLock
from time import sleep

import numpy as np
import zmq

from experimentor.config import settings
from experimentor.lib.log import get_logger

logger = get_logger(__name__)


class Pusher:
    """
    The Pusher is class that wraps some common methods of the ZMQ PUSH/PULL architecture.

    .. warning:: The main problem with this pattern is that if there is not PULL on the other side, a queue will build
        up on the PUSH side. This happens if, for example, we close the publisher but we keep generating data.
        Eventually the queue will outgrow the memory and the computer will crash.

    Parameters
    ----------
    port: int
        The port on which to connect the PUSH end. If not specified, it will grab the default value from settings

    Attributes
    ----------
    pusher: socket
        The socket where the communication happens

    i: int
        The number of messages that were pushed from a given

    topic_i: dict
        Number of data frames sent on each topic. For example: topic_i['topic']

    lock: RLOCK
        In case the same pusher is shared between different threads, this ensures the messages are sent in the proper
        block
    """
    def __init__(self, port=None):
        self.lock = RLock()
        context = zmq.Context()
        self.pusher = context.socket(zmq.PUSH)
        self.pusher.connect(f"tcp://127.0.0.1:{port or settings.PUBLISHER_PULL_PORT}")
        sleep(1)
        self.i = 0
        self.topic_i = {}
        atexit.register(self.finish)

    def publish(self, data, topic=""):
        """Publish data on a given topic. This is the core of the Pusher object.

        Parameters
        ----------
        data
            Data can be any Python object, provided that it is serializable

        topic: str
            The topic on which the data is being transmitted. If nothing is specified, it will be a broad transmission,
            meaning that every subscriber will receive it.

        """
        with self.lock:
            if topic in self.topic_i:
                self.topic_i[topic] += 1
            else:
                self.topic_i.update({topic: 1})

            if settings.PUBLISHER_READY:
                self.pusher.send_string(topic, zmq.SNDMORE)
                if isinstance(data, np.ndarray):
                    meta_data = dict(
                        numpy=True,
                        dtype=str(data.dtype),
                        shape=data.shape,
                        i=self.topic_i[topic]
                    )
                    self.pusher.send_json(meta_data, 0 | zmq.SNDMORE)
                    self.pusher.send(data, 0, copy=True, track=False)
                else:
                    meta_data = dict(
                        numpy=False
                    )
                    self.pusher.send_json(meta_data, 0 | zmq.SNDMORE )
                    self.pusher.send_pyobj(data)
                self.i += 1

    def finish(self):
        with self.lock:
            logger.info('Finishing Pusher')
            self.pusher.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    def __enter__(self):
        return self