"""
    Settings
    ========
    Experimentor relies on some general settings in order to run. For example, one can specify the port at which the
    publisher or pusher connects, or the window which is the starting point for the user interface. We specify some
    global parameres at :mod:`experimentor.config.global_settings`, that can be overriden at runtime by specifying the
    environmental variable `EXPERIMENTOR_SETTINGS_MODULE`.

    Only variables written in ALL CAPITAL LETTERS will be taken into account.

    .. note::
        The inspiration for this flow comes from `Django's Settings module<https://github.com/django/django/blob/c574bec0929cd2527268c96a492d25223a9fd576/django/conf/__init__.py>`_
"""

import importlib
import os

from experimentor.config import global_settings


class Settings:
    """ Loads the global parameters and overrides them with those specified in the settings module of the project.
    """
    def __init__(self, settings_module):
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        self.SETTINGS_MODULE = settings_module

        modifications = importlib.import_module(self.SETTINGS_MODULE)
        for setting in dir(modifications):
            if setting.isupper():
                setattr(self, setting, getattr(modifications, setting))


settings = Settings(os.environ.get('EXPERIMENTOR_SETTINGS_MODULE', 'experimentor.config.global_settings'))
