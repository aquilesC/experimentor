class Procedure:
    """Decorator to check the validity of a procedure before performing a measurement
    """
    def __init__(self, procedure):
        self.procedure = procedure

    def check_parameters(self, cls, *args, **kwargs):
        print(cls._parameters)

    def __call__(self, *args):
        self.check_parameters(args[0])
        return self.procedure(*args)