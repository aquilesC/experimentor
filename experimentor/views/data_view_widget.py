from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from experimentor.lib.log import get_logger


class DataViewWidget(QWidget):
    """ Base class that defines some common patterns for views which are meant to display data.

    Attributes
    -------
    default_Layout: By default, views will have a QHBoxLayout, it can be overriden when subclassing, or by changing the
        method get_layout

    data: This is the data being represented by the widget. This allows to define abstract methods for saving, regardless
        of what specific type of data it is.
    """
    default_layout = QHBoxLayout()

    def __init__(self, parent=None):
        super(DataViewWidget, self).__init__(parent=parent)

        self.setLayout(self.get_layout())
        self.logger = get_logger()

        self.data = None

    def get_layout(self):
        """ Returns the layout specified as the class attribute default_layout. Override this method to provide more
        complex behavior.
        """
        return self.default_layout
