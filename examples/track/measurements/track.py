from experimentor.core import Parameter, Procedure


class Track:
    exposure_time = Parameter(units='ms')
    roi = Parameter()
    binning = Parameter()
    background_mode = Parameter()

    @Procedure
    def timelapse(self):
        pass


