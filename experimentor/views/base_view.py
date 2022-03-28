"""
Base View
=========
All views defined in Experimentor should inherit from the ``BaseView`` class. This will homogenize the available
methods that make sense from within the framework. The core idea of the Base View is to be pure-Python, without
inheriting from any other Qt class. In this way, the BaseView can be used by any kind of view, either main windows,
widgets, dialogs, etc.
"""

from logging import warning

from experimentor.lib.log import get_logger
from experimentor.models.action import Action
from experimentor.views import try_except_dialog


class BaseView:
    """ Base class to homogenize what views are expected to do through the entire program cycle.
    """
    def __init__(self):
        self.logger = get_logger()
        self.logger.debug('Base View init')

    def connect_to_action(self, signal, action):
        if not isinstance(action, Action):
            warning(f'{action} is not an Action, consider using {signal}.connect instead')

        @try_except_dialog
        def handle_action(*args, **kwargs):
            action()

        signal.connect(handle_action)

