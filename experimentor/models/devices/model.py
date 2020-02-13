from experimentor.models.cameras.exceptions import DeviceModelException
from experimentor.models.models import BaseModel


class DeviceModel(BaseModel):
    def get_status(self) -> dict:
        """ Prepares the status of the device based on what is currently available in the
        model. It returns a dictionary with all the relevant information to bring the
        device to the same status in the future.

        :returns: dictionary with property-like values
        """
        if hasattr(self, 'Meta'):
            if hasattr(self.Meta, 'driver_type'):
                if self.Meta.driver_type == 'Lantz':
                    raise Warning('Not implemented yet')
                else:
                    raise DeviceModelException('This driver type is not supported for auto-generating the status')
        if hasattr(self, '_config'):
            return self._config
