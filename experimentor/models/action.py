"""
    Action
    ======

    An action is an event that gets triggered on a device. For example, a camera can have an action ``acquire`` or
    ``read``. They should normally be associated with the pressing of a button. Action is a handy decorator to register
    methods on a model and have quick access to them when building a user interface. They are multi-threaded by default
    however, they share the same lock. Therefore, if a device is able to run several actions simultaneously, it would be
    better to provide an explicit lock.

"""
import threading

from experimentor.models.models import ExpList


class Action:
    def __init__(self, method=None, **kwargs):
        self.method = method
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __set_name__(self, owner, name):
        model_actions = owner._actions
        if getattr(model_actions, 'model_name', None) != object.__qualname__:
            actions = model_actions.__class__(*model_actions)
            setattr(actions, 'model_name', object.__qualname__)
            owner._actions = actions

        owner._actions.append(name)

    def __call__(self, *args, **kwargs):
        if self.method is None and len(args) >= 1:
            return self.set_action(args[0])

        def run(method, instance):
            method(instance)

        with self.get_lock():
            self.thread = threading.Thread(target=run, args=(self.method, self.instance))
            self.thread.start()

    def get_lock(self):
        return self.kwargs.get('lock', self.instance._actions.lock)

    def set_action(self, method):
        return type(self)(method, **self.kwargs)


if __name__ == '__main__':
    from time import sleep

    class Test:
        _actions = ExpList()

        @Action()
        def test(self):
            sleep(2)
            print('Test')

    t = Test()
    print('1')
    t.test()
    print('2')
    t.test()
    print('3')
