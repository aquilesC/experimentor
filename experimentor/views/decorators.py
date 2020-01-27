from functools import wraps

from PyQt5.QtWidgets import QMessageBox


def try_except_dialog(func):
    """ Decorator to add to methods used in user interfaces. If there is a chance of an error appearing because of
    devices in the wrong state, etc. but the logic is not fail proof, you can use this decorator to display an error
    message with the stack trace instead of crashing the program.
    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            new_values = func(*args, **kwargs)
        except Exception as e:
            message = QMessageBox()
            message.setWindowTitle(f"Error with {func.__name__}")
            message.setText(f"{e}")
            message.exec()
            return
        return new_values
    return func_wrapper
