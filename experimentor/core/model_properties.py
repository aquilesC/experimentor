"""
Model Properties
================
Collection of decorators to make easier the interaction with properties of Models.

.. sectionauthor:: Aquiles Carattino
"""


class ModelProp:
    """Properties that belong to models. It makes easier the setting and getting of attributes, while at the same
    time it keeps track of the properties of each model.
    """

    name = ''
    kwargs = None

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self.kwargs = kwargs

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __set_name__(self, owner, name):
        self.name = name
        if not hasattr(owner, '_properties'):
            setattr(owner, '_properties', [])

        owner._properties.append(name)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def __call__(self, func):
        if self.fget is None:
            return self.getter(func)
        return self.setter(func)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__, **self.kwargs)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__, **self.kwargs)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__, **self.kwargs)

