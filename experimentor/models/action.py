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
    increment their usability::

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

    :license: MIT, see LICENSE for more details
    :copyright: 2020 Aquiles Carattino
"""
from concurrent.futures.thread import ThreadPoolExecutor

import threading


class Action:
    """ Decorator for methods in models. Actions are useful when working with methods that run once, and are normally
    associated with pressing of a button. Actions are multi-threaded by default, using a single executor that returns a
    future.

    Even though Actions (intended as the method in a model) can take arguments, it may be a better approach to store
    the parameters as attributes before triggering an action. In this way, triggering an action would be equivalent to
    pressing a button. In the same way, actions can store return values as attribute in the model itself, avoiding the
    need to keep track of the future returned by the action. Be aware of potential racing conditions that may arise when
    using shared memory to exchange information.

    .. todo:: Define a clear protocol for exchanging information with models. Should it be state-based (i.e. storing
        parameters as attributes in the class) or statement based (i.e. passing parameters as arguments of methods).
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

        run = self.get_run()
        return run(self.method, self.instance, *args, **kwargs)

    def get_run(self):
        """ Generates the run function that will be applied to the method. It looks a big convoluted, but it is one of
        the best approaches to make it easy to extend the Actions in the longer run. The return callable grabs the
        executor from the method :func:`self.get_executor`.

        Returns
        -------
        callable
            A function that takes two arguments: method and instance and that submits them to an executor
        """

        def run(method, instance, *args, **kwargs):
            executor = self.get_executor()
            return executor.submit(method, instance, *args, **kwargs)

        return run

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
        """ Wrapper that returns this own class but initializes it with a method and a previously stored dict of kwargs.
        This method is what happens when the Action itself is defined with arguments.

        Parameters
        ----------
        method: callable
            The method that is decorated by the Action

        Returns
        -------
        Action
            Returns an instance of the Action using the previously stored kwargs but adding the method
        """
        return type(self)(method, **self.kwargs)
