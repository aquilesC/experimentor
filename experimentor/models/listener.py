from time import sleep
import zmq

from experimentor.config.settings import *
from experimentor.lib.log import get_logger


class Listener:
    def __init__(self):
        context = zmq.Context()
        self.listener = context.socket(zmq.PUSH)
        self.listener.connect(f"tcp://127.0.0.1:{PUBLISHER_PULL_PORT}")
        sleep(1)
        self.logger = get_logger()

    def publish(self, data, topic=""):
        self.listener.send_string(topic, zmq.SNDMORE)
        self.listener.send_pyobj(data)

    def finish(self):
        self.logger.info('Finishing listener')
        self.listener.close()