class Procedure:
    def __init__(self,
                 fsetup=None,
                 frun=None,
                 fstart=None,
                 ffinalize=None,
                 **kwargs,
                 ):

        self.fsetup = fsetup
        self.frun = frun
        self.fstart = fstart
        self.ffinalize = ffinalize
        self.kwargs = kwargs

    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner
        if owner is not None:
            if not hasattr(owner, '_procedures'):
                owner._procedures = {self.name: self}
            else:
                owner._procedures.update({self.name: self})

    def __get__(self, instance, owner):
        if instance is None:
            return self
        self.instance = instance
        return instance._procedures[self.name]

    def __set__(self, instance, value):
        raise AttributeError('You can\'t set a Procedure')

    def setup(self, fsetup):
        print('Setting Up')
        return type(self)(fsetup, self.frun, self.fstart, self.ffinalize, **self.kwargs)

    def run(self, frun):
        print('Running')
        return type(self)(self.fsetup, frun, self.fstart, self.ffinalize, **self.kwargs)

    def start(self, fstart):
        print('Starting')
        return type(self)(self.fsetup, self.frun, fstart, self.ffinalize, **self.kwargs)

    def __call__(self, *args, **kwargs):
        print('Running on', self.instance, id(self.instance))
        self.fsetup(self.instance, *args, **kwargs)
        self.fstart(self.instance, *args, **kwargs)
        self.frun(self.instance, *args, **kwargs)


class Experiment:
    name = 'Experiment'

    measure = Procedure()

    @measure.setup
    def measure(self):
        print('Really Setting Up')

    @measure.run
    def measure(self):
        print('Really Running')
        print(self.name)

    @measure.start
    def measure(self):
        print('Really Starting')

print(id(Experiment))
experiment = Experiment()
exp2 = Experiment()
print(id(experiment))
print(id(exp2))
experiment.measure()
exp2.measure()
experiment.measure()