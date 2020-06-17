"""
    Data Source
    ===========

    These objects are defined in models and are meant to be used to broadcast information across different objects,
    either on different threads, processes, or computers. In their core, they are ZMQ Publishers and hold the necessary
    information in order to create a subscriber based on them.
"""


class DataSource:
    def __init__(self):
        pass

    def connect(self):
        pass

    def initialize(self):
        pass

    def finalize(self):
        pass

    def __set_name__(self, owner, name):
        print(f'Owner: {owner}, name: {name}')

    def __get__(self, instance, owner):
        pass

