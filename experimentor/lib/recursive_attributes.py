""" Functions to get and set attributes of nested objects. These functions allow to do things like:

>>> rgetattr(obj, 'sub1.sub2.attr')

Taken from: https://stackoverflow.com/a/31174427/4467480
"""
import functools


def rsetattr(obj, attr, val):
    """ Iteratively gets attributes of objects until the last level and then sets its value.
    """
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    """ Recursive get attribute of objects.
    """
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))