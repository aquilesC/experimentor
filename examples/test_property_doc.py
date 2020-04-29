class Test:
    """ This is the class """
    _prop = 1

    @property
    def prop(self):
        """ This is the getter """
        return self._prop

    @prop.setter
    def prop(self, val):
        """ This is the setter """
        self._prop = val

