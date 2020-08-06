"""
Model Exceptions
================

:license: MIT, see LICENSE for more details
:copyright: 2020 Aquiles Carattino
"""
class ExperimentorException(Exception):
    """Base exception for all experimentor modules"""
    pass


class ModelException(ExperimentorException):
    pass


class PropertyException(ModelException):
    pass


class LinkException(PropertyException):
    pass


class SignalException(ExperimentorException):
    pass