"""
Measurement Classes
===================

Collection of classes useful for developing the logic of a measurement

.. sectionauthor:: Aquiles Carattino
"""
from numbers import Number

from pint.errors import UndefinedUnitError

from experimentor import Q_
from experimentor.core.exceptions import DuplicatedParameter


class Parameter:
    """Parameters that belong to a measurement. They allow to define units, limits and ui_classes.
    """

    name = ''

    def __set_name__(self, owner, name):
        self.name = name
        if not hasattr(owner, '_parameters'):
            setattr(owner, '_parameters', [])

        if name in owner._parameters:
            raise DuplicatedParameter(f'{name} already exists in {owner}')
        owner._parameters.append(name)

    def __init__(self, units=None, ui_class=None):
        self._value = None

        self.units = None
        if units:
            if isinstance(units, Q_):
                self.units = units
            else:
                try:
                    self.units = Q_(units)
                except UndefinedUnitError:
                    self.units = None

        self.ui_class = ui_class

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        if self.units:
            if isinstance(value, Q_):
                value = value.to(self.units)
            elif isinstance(value, str):
                value = Q_(value).to(self.units)
            elif isinstance(value, Number):
                value = value * self.units
            else:
                raise Exception(f'Cant set {self.name} to {value}')

        self._value = value


if __name__ == '__main__':
    class Test:
        param = Parameter(units='nm')

    t = Test()
    print(t.param)
    t.param = 5
    print(t.param)
    t.param = '5mm'
    print(t.param)

