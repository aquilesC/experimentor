from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout

from experimentor.lib.log import get_logger
from experimentor.views.exceptions import ViewException


class DataViewWidget(QWidget):
    """ Base class that defines some common patterns for views which are meant to display data.

    Attributes
    ----------
    default_Layout: By default, views will have a QHBoxLayout, it can be overriden when subclassing, or by changing the
        method get_layout

    data: This is the data being represented by the widget. This allows to define abstract methods for saving, regardless
        of what specific type of data it is.
    """
    default_layout = 'horizontal'

    def __init__(self, parent=None):
        super(DataViewWidget, self).__init__(parent=parent)
        self.logger = get_logger()

        self._layout = None
        self.set_layout()
        self.data = None

    def set_layout(self):
        if self._layout is None:
            self.logger.info(f'Setting layout to: {self.default_layout}')
            if self.default_layout == 'horizontal':
                self._layout = QHBoxLayout(self)
            elif self.default_layout == 'vertical':
                self._layout = QVBoxLayout(self)
            elif self.default_layout == 'grid':
                self._layout = QGridLayout(self)
            else:
                raise ViewException(f'Layout {self.layout} not implemented. Options are horizontal, vertical, grid')
            self.setLayout(self._layout)
        return self.get_layout()

    def get_layout(self):
        """ Returns the layout specified as the class attribute default_layout. Override this method to provide more
        complex behavior.
        """
        return self._layout
