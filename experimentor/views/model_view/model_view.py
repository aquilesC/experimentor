from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QFormLayout

from experimentor.models.devices.base_device import ModelDevice


class ModelViewWidget(QWidget):
    def __init__(self, model: ModelDevice, parent=None):
        super().__init__(parent=parent)
        self.layout = None
        self.model = model

        self.set_layout()
        self.model_to_layout()

    def get_layout(self):
        return QFormLayout()

    def set_layout(self):
        self.layout = self.get_layout()
        self.setLayout(self.layout)

    def model_to_layout(self):
        params = self.model.config.all()
        for param, value in params.items():
            param_widget = QWidget()
            param_widget_layout = QHBoxLayout()
            param_widget.setLayout(param_widget_layout)
            label = QLabel(param)
            value_line = QLineEdit(str(value))
            param_widget_layout.addWidget(label)
            param_widget_layout.addWidget(value_line)
            self.layout.addRow(label, value_line)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication


    model = ModelDevice()
    model.config['test1'] = 1
    model.config['test_2'] = 2
    model.config['value'] = 3.14
    app = QApplication([])
    win = ModelViewWidget(model)
    win.show()
    app.exec()