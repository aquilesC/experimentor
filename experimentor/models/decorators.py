"""
Decorators
==========
Useful decorators for models.

:license: MIT, see LICENSE for more details
:copyright: 2020 Aquiles Carattino
"""
from functools import wraps
from threading import Thread

from experimentor.lib.log import get_logger
from experimentor.models.models import BaseModel


def not_implemented(func):
    """ Raises a warning in the logger in case the method was not implemented by child classes, but it does not prevent
    the program from running.
    """
    @wraps(func)
    def func_wrapper(cls, *args, **kwargs):
        logger = get_logger(__name__)
        logger.warning(f'{func.__name__} from {cls} not Implemented')
        return func(cls, *args, **kwargs)
    return func_wrapper


def make_async_thread(func):
    """ Simple decorator to make a method run on a separated thread. This decorator will not work on simple
    functions, since it requires the first argument to be an instantiated class (self).
    It will store the method in an attribute of the class, called `_threads``, or it will create it if it does not
    exist yet.

    TODO: Check what happens with the _thread list and inherited classes. Is there a risk that the list will be
        shared? If the list is defined as a class attribute instead of an object attribute, most likely it will. If
        it is defined outside of the scope and then linked to the class, also.

    .. warning:: In complex scenarios, this simple decorator can give raise to mistakes, i.e. objects having access
        to other objects threads.

    .. TODO: May be wise to use this decorator only with certain models, and define a method directly in them to
        manipulate the threads, avoiding the inherent problems of mutable types.

    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        logger = get_logger(name=__name__)
        logger.info('Starting new thread for {}'.format(func.__name__))
        if isinstance(args[0], BaseModel):
            args[0].clean_up_threads()

        if not hasattr(args[0], '_threads'):
            args[0]._threads = []

        elif not isinstance(args[0]._threads, list):
            raise ValueError('The variable _threads must be a list in order to store a new Thread in it')

        args[0]._threads.append([func.__name__, Thread(target=func, args=args, kwargs=kwargs)])
        args[0]._threads[-1][1].start()
        logger.info('In total there are {} threads'.format(len(args[0]._threads)))

    return func_wrapper


def avoid_repeat(func):
    @wraps(func)
    def func_wrapper(cls, *args, **kwargs):
        logger = get_logger(name=__name__)
        logger.info(f'Checking if function {func.__name__} was already triggered')
        update = False
        if hasattr(cls, 'cache_setters'):
            if len(args) >= 1:
                for i, arg in enumerate(args[1:]):
                    old_arg = args[0].cache_setters.get('args')[i]
                    if arg != old_arg:
                        update = True
            if len(kwargs) > 1:
                for key, value in kwargs.items():
                    old_value = args[0].cache_setters.get('kwargs')[key]
                    if value != old_value:
                        update = True
        else:
            cls.cache_setters = dict()
            update = True

        if update:
            cls.cache_setters.update({'args': args, 'kwargs': kwargs})
            logger.info('Updating values')
            return func
        else:
            logger.info('Nothing to update')
            return lambda *args, **kwargs: None

    return func_wrapper