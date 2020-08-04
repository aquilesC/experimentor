__version__ = '0.3.0'

from multiprocessing import Event

from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

general_stop_event = Event()  # This event is the last resource to stop threads and processes

__all__ = [
    'config',
    'core',
    'drivers',
    'lib',
    'models',
    'views',
]