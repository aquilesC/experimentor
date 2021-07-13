# ##############################################################################
#  Copyright (c) 2021 Aquiles Carattino, Dispertech B.V.                       #
#  test_view_components.py is part of Experimentor.                            #
#  This file is released under an MIT license.                                 #
#  See LICENSE.MD for more information.                                        #
# ##############################################################################
import unittest

from PyQt5.QtWidgets import QApplication

from experimentor.views.components import FileSelector


class TestViewComponents(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.file_selector_widget = FileSelector()

    def test_path(self):
        self.file_selector_widget.path_line.setText('Test')
        self.assertEqual(self.file_selector_widget.path, 'Test')