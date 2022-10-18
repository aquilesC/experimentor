__version__ = '0.4.1'

from multiprocessing import Event

from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

general_stop_event = Event()  # This event is the last resource to stop threads and processes

from experimentor.views.camera.camera_viewer_widget import CameraViewerWidget as CameraView

__all__ = [
    'config',
    'core',
    'drivers',
    'lib',
    'models',
    'views',
]