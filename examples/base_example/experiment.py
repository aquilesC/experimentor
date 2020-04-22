from experimentor.core.signal import Signal
from experimentor.models.experiments import Experiment


class Exp(Experiment):
    signal = Signal()

    def __init__(self):
        super().__init__(filename=None)
        self.signal.connect(self.print_something)

    def initialize(self):
        self.signal.connect(self.print_something)

    def print_something(self, *args):
        print('something')
