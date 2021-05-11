"""
Camera Viewer Widget
====================
Wrapper around PyQtGraph ImageView.

"""
import numpy as np
import pyqtgraph as pg

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QAction, QVBoxLayout, QPushButton
from pyqtgraph import GraphicsLayoutWidget

from experimentor.lib.log import get_logger
from experimentor.views.data_view_widget import DataViewWidget


class CameraViewerWidget(DataViewWidget):
    """ The Camera Viewer Widget is a wrapper around PyQtGraph ImageView. It adds some common methods for getting extra
    mouse interactions, such as performing an auto-range through right-clicking, it allows to drag and drop horizontal
    and vertical lines to define a ROI, and it allows to draw on top of the image. The core idea is to make these options
    explicit, in order to systematize them in one place.

    Signals
    -------
    clicked_on_image: Emits [float, float] with the coordinates where the mouse was clicked on the image. Does not
        distinguish between left/right clicks. Any further processing must be done downstream.

    Attributes
    ----------
    layout: QHBoxLayout, in case extra elements must be added
    viewport: GraphicsLayoutWidget
    view: ViewBox
    img: ImageItem
    imv: ImageView
    auto_levels: Whether to actualize the levels of the image every time they are refreshed
    """

    clicked_on_image = pyqtSignal([float, float])

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Settings for the image
        self.viewport = GraphicsLayoutWidget()
        self.view = self.viewport.addViewBox(lockAspect=False, enableMenu=True)

        self.img = pg.ImageItem()
        self.view.addItem(self.img)
        self.imv = pg.ImageView(view=self.view, imageItem=self.img)

        self.scene().sigMouseClicked.connect(self.mouse_clicked)

        # Add everything to the widget
        layout = self.get_layout()
        layout.addWidget(self.imv)

        self.show_roi_lines = False  # ROI lines are shown or not
        self.show_cross_hair = False  # Cross hair is shown or not
        self.show_cross_cut = False  # Cross cut is shown or not
        self.cross_hair_setup = False  # Cross hair was setup or not
        self.cross_cut_setup = False  # Cross cut was setup or not

        self.rois = []

        self.corner_roi = [0, 0]  # Initial ROI corner for the camera

        self.first_image = True

        self.logger = get_logger()

        self.last_image = None

        self.add_actions_to_menu()
        self.setup_mouse_tracking()

    def scene(self):
        """ Shortcut to getting the image scene"""
        return self.img.scene()

    def update_image(self, image, auto_range=False, auto_histogram_range=False):
        """ Updates the image being displayed with some sensitive defaults, which can be over written if needed.
        """
        auto_levels = self.auto_levels_action.isChecked()
        self.logger.debug(f'Updating image with auto_levels: {auto_levels}')
        if image is not None:
            self.imv.setImage(image, autoLevels=auto_levels, autoRange=auto_range, autoHistogramRange=auto_histogram_range)
            if self.first_image:
                self.do_auto_range()
                self.first_image = False
            self.last_image = image
        else:
            self.logger.debug(f'No new image to update')

    def setup_roi_lines(self, max_size=None):
        """Sets up the ROI lines surrounding the image.
        
        :param list max_size: List containing the maximum size of the image to avoid ROIs bigger than the CCD."""
        if self.last_image is None:
            return
        self.logger.info('Setting up ROI lines')

        if not isinstance(max_size, list):
            max_size = self.last_image.shape

        self.hline1 = pg.InfiniteLine(angle=0, movable=True, hoverPen={'color': "FF0", 'width': 4})
        self.hline2 = pg.InfiniteLine(angle=0, movable=True, hoverPen={'color': "FF0", 'width': 4})
        self.vline1 = pg.InfiniteLine(angle=90, movable=True, hoverPen={'color': "FF0", 'width': 4})
        self.vline2 = pg.InfiniteLine(angle=90, movable=True, hoverPen={'color': "FF0", 'width': 4})

        self.hline1.setValue(0)
        self.vline1.setValue(0)
        self.vline2.setValue(max_size[0])
        self.hline2.setValue(max_size[1])
        self.hline1.setBounds((0, max_size[1]))
        self.hline2.setBounds((0, max_size[1]))
        self.vline1.setBounds((0, max_size[0]))
        self.vline2.setBounds((0, max_size[0]))
        self.view.addItem(self.hline1)
        self.view.addItem(self.hline2)
        self.view.addItem(self.vline1)
        self.view.addItem(self.vline2)
        self.corner_roi[0] = 0
        self.corner_roi[1] = 0

    def get_roi_values(self):
        """ Get's the ROI values in camera-space. It keeps track of the top left corner in order
        to update the values before returning.
        :return: Position of the corners of the ROI region assuming 0-indexed cameras.
        """
        y1 = round(self.hline1.value())
        y2 = round(self.hline2.value())

        x1 = round(self.vline1.value())
        x2 = round(self.vline2.value())

        width = np.abs(x1-x2)
        height = np.abs(y1-y2)
        x = np.min((x1, x2)) + self.corner_roi[0]
        y = np.min((y1, y2)) + self.corner_roi[1]
        return (x, width), (y, height)

    def set_roi_lines(self, X, Y):
        self.corner_roi = [X[0], Y[0]]
        self.hline1.setValue(0)
        self.vline1.setValue(0)
        self.hline2.setValue(Y[1])  # To the last pixel
        self.vline2.setValue(X[1])  # To the last pixel

    def setup_mouse_tracking(self):
        self.imv.setMouseTracking(True)
        self.imv.getImageItem().scene().sigMouseMoved.connect(self.mouseMoved)
        self.imv.getImageItem().scene().contextMenu = None

    def keyPressEvent(self,key):
        """Triggered when there is a key press with some modifier.
        Shift+C: Removes the cross hair from the screen
        These last two events have to be handeled in the mainWindow that implemented this widget."""
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            if key.key() == 67:  # For letter C of 'Clear
                if self.show_cross_hair:
                    for c in self.crosshair:
                        self.view.removeItem(c)
                    self.show_cross_hair = False
                if self.show_cross_cut:
                    self.view.removeItem(self.crossCut)
                    self.show_cross_cut = False

    def mouseMoved(self, arg):
        """Updates the position of the cross hair. The mouse has to be moved while pressing down the Ctrl button."""
        # arg = evt.pos()
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if self.cross_hair_setup:
                if not self.show_cross_hair:
                    for c in self.crosshair:
                        self.view.addItem(c)
                    self.show_cross_hair = True
                self.crosshair[1].setValue(int(self.img.mapFromScene(arg).x()))
                self.crosshair[0].setValue(int(self.img.mapFromScene(arg).y()))
        elif modifiers == Qt.AltModifier:
            self.logger.debug('Moving mouse while pressing Alt')
            if self.cross_cut_setup:
                if not self.show_cross_cut:
                    self.view.addItem(self.crossCut)
                self.show_cross_cut = True
                self.crossCut.setValue(int(self.img.mapFromScene(arg).y()))

    def do_auto_range(self):
        """ Sets the levels of the image based on the maximum and minimum. This is useful when auto-levels are off
        (the default behavior), and one needs to quickly adapt the histogram.
        """

        h, y = self.img.getHistogram()
        self.imv.setLevels(min(h),max(h))

    def draw_target_pointer(self, locations):
        """gets an image and draws a circle around the target locations.

        :param DataFrame locations: DataFrame generated by trackpy's locate method. It only requires columns `x` and `y` with coordinates.
        """
        if locations is None:
            return

        locations = locations[['y', 'x']].values
        brush = pg.mkBrush(color=(255, 0, 0))
        self.marker.setData(locations[:, 0], locations[:, 1], symbol='x', symbolBrush=brush)

    def setup_cross_hair(self, max_size):
        """Sets up a cross hair."""
        self.show_cross_hair = self.setup_cross_hair_action.isChecked()
        if self.last_image is None:
            return
        self.logger.info('Setting up Cross Hair lines')

        if not isinstance(max_size, list):
            max_size = self.last_image.shape

        self.cross_hair_setup = True
        self.crosshair = []
        self.crosshair.append(pg.InfiniteLine(angle=0, movable=False, pen={'color': 124, 'width': 4}))
        self.crosshair.append(pg.InfiniteLine(angle=90, movable=False, pen={'color': 124, 'width': 4}))
        self.crosshair[0].setBounds((1, max_size[1] - 1))
        self.crosshair[1].setBounds((1, max_size[0] - 1))

    def setup_cross_cut(self, max_size):
        """Set ups the horizontal line for the cross cut."""
        self.show_cross_cut = self.setup_cross_cut_action.isChecked()
        if self.last_image is None:
            return
        self.logger.info('Setting up horizontal cross cut line')

        if not isinstance(max_size, list):
            max_size = self.last_image.shape[1]

        self.cross_cut_setup = True
        self.crossCut = pg.InfiniteLine(angle=0, movable=False, pen={'color': 'g', 'width': 2})
        self.crossCut.setBounds((1, max_size))

    def mouse_clicked(self, evnt):
        modifiers = evnt.modifiers()
        if modifiers == Qt.ControlModifier:
            self.clicked_on_image.emit(self.img.mapFromScene(evnt.pos()).x(), self.img.mapFromScene(evnt.pos()).y())

    def add_actions_to_menu(self):
        """ Adds actions to the contextual menu. If you want to have control on which actions appear, consider subclassing
        this widget and overriding this method.
        """
        self.auto_range_action = QAction("Auto Range", self.view.menu)
        self.auto_range_action.triggered.connect(self.do_auto_range)

        self.setup_roi_lines_action = QAction("Setup ROI", self.view.menu)
        self.setup_roi_lines_action.triggered.connect(self.setup_roi_lines)

        self.setup_cross_cut_action = QAction("Setup cross cut", self.view.menu, checkable=True)
        self.setup_cross_cut_action.triggered.connect(self.setup_cross_cut)

        self.setup_cross_hair_action = QAction("Setup cross hair", self.view.menu, checkable=True)
        self.setup_cross_hair_action.triggered.connect(self.setup_cross_hair)

        self.auto_levels_action = QAction('Auto Levels', self.view.menu, checkable=True)
        self.view.menu.addAction(self.auto_range_action)
        self.view.menu.addAction(self.auto_levels_action)
        self.view.menu.addAction(self.setup_roi_lines_action)
        self.view.menu.addAction(self.setup_cross_hair_action)
        self.view.menu.addAction(self.setup_cross_cut_action)

    @classmethod
    def connect_to_camera(cls, camera, refresh_time=50, parent=None):
        """ Instantiate the viewer using connect_to_camera in order to get some functionality out of the box. It will
        create a timer to automatically update the image
        """
        instance = cls(parent=parent)
        instance.timer = QTimer()
        instance.timer.timeout.connect(lambda: instance.update_image(camera.temp_image))
        instance.timer.start(refresh_time)
        return instance