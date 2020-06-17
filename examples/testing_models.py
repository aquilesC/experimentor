import time

from experimentor.core.signal import Signal
from experimentor.core.subscriber import Subscriber
from experimentor.models import BaseModel


def func():
    print('Func')


class MySignal:
    def __init__(self, func):
        if hasattr(func, '__self__'):
            print(func.__self__)
        else:
            print(func)


class MyModel(BaseModel):
    signal = Signal()
    other_signal = Signal()
    def __init__(self):
        super().__init__()
        self.s = Subscriber(self.do_something, self.signal.url, self.signal.name)

    def do_something(self, *args, **kwargs):
        print('Do something')


my_model = MyModel()
for signal in my_model._signals:
    print(signal)

time.sleep(2)
my_model.signal.emit('payload')