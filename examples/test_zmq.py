from time import sleep

from experimentor.config import settings
from experimentor.config.global_settings import PUBLISHER_EXIT_KEYWORD
from experimentor.core.publisher import Publisher
from experimentor.core.subscriber import Subscriber
from experimentor.models.listener import Listener


def test_subscriber(data):
    print(data)


p = Publisher(settings.GENERAL_STOP_EVENT)
p.start()
s = Subscriber(test_subscriber, "Topic1", [], {})
s.start()
s2 = Subscriber(test_subscriber, "Topic2", [], {})
s2.start()
sleep(3)
l = Listener()
data = "Data 2"
l.publish(data, "Topic2")
data = "Data 1"
l.publish(data, "Topic1")
l.publish(PUBLISHER_EXIT_KEYWORD)


for sub in Subscriber._get_instances():
    print(sub.topic)