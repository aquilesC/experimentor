# ##############################################################################
#  Copyright (c) 2021 Aquiles Carattino, Dispertech B.V.                       #
#  file_selector.py is part of Experimentor.                                   #
#  This file is released under an MIT license.                                 #
#  See LICENSE.MD for more information.                                        #
# ##############################################################################
"""
Widget for selecting a file. It implements a line edit and a button to open a file selector.

TODO: It is a very basic widget to abstract a common pattern. However, it does not have flexibility to filter by file
    type, change the button icon, etc.
"""
from PyQt5.QtWidgets import QHBoxLayout, QSizePolicy, QWidget, QLineEdit, QPushButton, QFileDialog


class FileSelector(QWidget):
    """
    Widget to select an existing file, for example to open it or to append data to it.

    Attributes
    ----------
    path : str
        Shorthand for the path_line.text() method.
    path_line : QLineEdit
        It displays the full path to the selected file
    button : QPushButton
        The button that triggers the file selection dialog

    Methods
    -------
    open_file_dialog()
        Slot that is triggered by the clicking of the button. It opens that file dialog and updates the line
    """
    def __init__(self, parent=None):
        super(FileSelector, self).__init__(parent=parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.path_line = QLineEdit()
        self.button = QPushButton()

        self.button.setText('...')
        self.button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.layout.addWidget(self.path_line)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        """
        When the button is clicked, it opens the QFileDialog window. If there is a path specified, the window
        will open in that position, if not, it will open in the default path (most likely the file path).
        Once a file is selected, it updates the line with the path to the file.

        """
        if self.path != '':
            selected = QFileDialog.getOpenFileName(self, directory=self.path)
        else:
            selected = QFileDialog.getOpenFileName(self)

        self.path_line.setText(selected[0])
        self.path_line.end(False)

    @property
    def path(self):
        return self.path_line.text()