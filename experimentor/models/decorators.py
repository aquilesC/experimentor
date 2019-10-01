from functools import wraps
from threading import Thread

from experimentor.lib.log import get_logger



def not_implemented(func):
    @wraps(func)
    def func_wrapper(cls, *args, **kwargs):
        logger = get_logger(__name__)
        logger.warning(f'{cls}.{func.__name__} Not Implemented')
        return func(cls, *args, **kwargs)
    return func_wrapper


def make_async_thread(func):
    """ Simple decorator to make a method run on a separated thread. It requires that the class has a property
    called ``_threads`` which is a list and holds all the running threads.
    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        logger = get_logger(name=__name__)
        logger.info('Starting new thread for {}'.format(func.__name__))
        if not hasattr(args[0], '_threads'):
            args[0]._threads = []
        args[0]._threads.append([func.__name__, Thread(target=func, args=args, kwargs=kwargs)])
        args[0]._threads[-1][1].start()
        logger.info('In total there are {} threads'.format(len(args[0]._threads)))

    return func_wrapper