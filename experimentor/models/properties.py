import warnings
from typing import List

from experimentor.models.exceptions import LinkException, PropertyException


class Properties:
    """ Class to store the properties of models. It keeps track of changes in order to monitor whether a specific value
    needs to be updated. It also allows to keep track of what method should be triggered for each update.
    """

    def __init__(self, **kwargs):
        self._properties = dict()
        self._links = dict()
        if kwargs:
            for key, value in kwargs.items():
                self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if key not in self._properties:
            self._properties.update({
                key:
                    {
                        'new_value': value,
                        'value': None,
                        'old_value': None,
                        'to_update': True
                    }
                })
        else:
            self._properties[key].update({
                'new_value': value,
                'to_update': True,
            })

    def __getitem__(self, item):
        if isinstance(item, int):
            key = list(self._properties.keys())[item]
            return self._properties[key]['value']
        return self._properties[item]['value']

    def update(self, values: dict):
        """Updates the values in the same way the update method of a dictionary works. It, however, stores the values
        as a new value, it does not alter the values stored. For updating the proper values use :func:`self.upgrade`
        """
        for key, value in values.items():
            self.__setitem__(key, value)

    def upgrade(self, values: dict):
        """This method actually overwrites the values stored in the properties. This method should be used only when the
        real values generated by a device are known, for example. It will also change the new values to values, and will
        set the ``to_update`` to false.
        """
        for key, value in values.items():
            if key not in self._properties:
                raise PropertyException(f'Trying to upgrade {key} but is not a listed property')
            self._properties[key].update({
                'new_value': value,
                'value': value,
                'to_update': False,
            })

    def get(self, prop: str) -> dict:
        """Get the information of a given property, including the new value, value, old value and if it is marked as to
        be updated.
        """
        return self._properties[prop]

    def to_update(self) -> dict:
        """Returns a dictionary containing all the properties marked to be updated. """
        props = {}
        for key, values in self._properties.items():
            if values['to_update']:
                props[key] = values
        return props

    def link(self, linking: dict) -> None:
        """Link properties to methods for update and retrieve them.

        :param linking: Dictionary in where information is stored as parameter=>method, for example:
            linking = {'exposure_time': 'exposure'}
            In this case, ``exposure_time`` is the property stored, while ``exposure`` is the method that will be called
            for updating.
        """
        for key, value in linking.items():
            if key in self._links and self._links[key] is not None:
                raise LinkException(f'That property is already linked to {self._links[key]}. Please, unlink first')
            self._links[key] = value

    def unlink(self, unlink_list: List[str]) -> None:
        """ Unlinks the properties and the methods. This is just to prevent overwriting linkings under the hood and
        forcing the user to actively unlink before linking again.

        :param unlink_list: List containing the names of the properties to be unlinked.
        """

        for link in unlink_list:
            if link in self._links:
                self._links[link] = None
            else:
                warnings.warn('Unlinking a property which was not previously linked.')

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Properties object from a dictionary"""
        return cls(**data)

    def __repr__(self):
        return repr(self._properties)
