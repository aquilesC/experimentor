class Experiment:
    _models = []
    _measurements = []

    def register_models(self, *args):
        for arg in args:
            self._models.append(arg)

    def register_measurements(self, *args):
        for arg in args:
            self._measurements.append(arg)