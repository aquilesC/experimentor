"""
    Settings
    ========
    Core classes and functions to handle configurations in an Experimentor project. There is still a lot of work to do
    to make it more robust and extensible, especially when overriding values given by default in the application.

"""
from experimentor.config import global_settings


class Settings:
    def __init__(self):
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))


settings = Settings()
