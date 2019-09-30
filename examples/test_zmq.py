from time import sleep

from experimentor.config.settings import GENERAL_STOP_EVENT, PUBLISHER_EXIT_KEYWORD
from experimentor.models.listener import Listener
from experimentor.models.publisher import Publisher
from experimentor.models.subscriber import Subscriber


def test_subscriber(data):
    print(data)


p = Publisher(GENERAL_STOP_EVENT)
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