from PyQt5.QtWidgets import QPushButton


class ToggableButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(ToggableButton, self).__init__(*args, **kwargs)

        self.status = 0
        self.clicked.connect(self.toggle)
        self.toggle()

    def toggle(self):
        self.status = 0 if self.status else 1
        if self.status:
            self.setStyleSheet("background-color: green")
        else:
            self.setStyleSheet("background-color: red")