"""
    Action
    ======

    An action is an event that gets triggered on a device. For example, a camera can have an action ``acquire`` or
    ``read``. They should normally be associated with the pressing of a button. Action is a handy decorator to register
    methods on a model and have quick access to them when building a user interface. They are multi-threaded by default,
    however, they share the same executor, defined at the model-level. Therefore, if a device is able to run several
    actions simultaneously, different executors can be defined at the moment of Action instantiation.

    To extend Actions, the best is to sub class it and re implement the ``get_executor`` method, or any other method
    relevant to change the expected behavior.

    Examples
    ---------
    A general purpose model can implement two methods: ``initialize`` and ``auto_calibrate``, we can use the Actions to
    increment their usability:

    class TestModel:
        @Action
        def initialize(self):
            print('Initializing')

        @Action
        def auto_calibrate(self):
            print('Auto Calibrating')

    tm = TestModel()
    tm.initialize()
    tm.auto_calibrate()
    print(tm.get_actions())

"""
from concurrent.futures.thread import ThreadPoolExecutor

import threading
from experimentor.models.models import ExpList


class Action:
    """ Decorator for methods in models. Actions are useful when working with methods that run once, and are normally
    associated with pressing of a button. Actions are multi-threaded by default, using a single executor that returns a
    future.

    Actions themselves do not take arguments, the model should be set before triggering the action. In the same way,
    they should not return any values. In case there is need to share data to and from actions, the best is to change
    attributes in the model itself. Be aware that using the simple shared-memory approach to exchange information
    between threads may give raise to some racing conditions in extreme situations.
    """
    def __init__(self, method=None, **kwargs):
        self.method = method
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __set_name__(self, owner, name):
        model_actions = owner.get_actions()
        if getattr(model_actions, 'model_name', None) != object.__qualname__:
            actions = model_actions.__class__(*model_actions)
            setattr(actions, 'model_name', object.__qualname__)
            setattr(actions, 'lock', threading.Lock())
            setattr(actions, 'executor', ThreadPoolExecutor(max_workers=1))
            owner.set_actions(actions)

        owner.get_actions().append(name)

    def __call__(self, *args, **kwargs):
        if self.method is None and len(args) >= 1:
            return self.set_action(args[0])

        def run(method, instance):
            executor = self.get_executor()
            return executor.submit(method, instance)

        return run(self.method, self.instance)

    def get_executor(self):
        """ Gets the executor either explicitly defined as an argument when instantiating the Action, or grabs it from
         the parent instance, and thus is shared between all action in a model.

         To change the behavior, subclass Action and overwrite this method.
         """
        return self.kwargs.get('executor', self.instance._actions.executor)

    def get_lock(self):
        """ Gets the lock specified in the keyword arguments while creating the Action, or defaults to the lock stored
        in the instance and thus shared between all actions in the model.

        .. deprecated:: 0.3.0
            Since v0.3.0 we are favoring concurrent.futures instead of lower-level threading for Actions.
        """
        return self.kwargs.get('lock', self.instance._actions.lock)

    def set_action(self, method):
        return type(self)(method, **self.kwargs)
