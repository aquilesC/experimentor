# -*- coding: utf-8 -*-
"""
    Decorators
    ==========
    Decorators are very useful tools to enhance the behavior of simple methods and functions. Experimentor has
    abstracted some of the most common patterns such that it becomes very simple for a developer to add complex
    functionality into their own program.
"""
from functools import wraps
from multiprocessing import Process
from threading import Thread

from experimentor.lib.log import get_logger


def make_async_thread(func):
    """ Simple decorator to make a method run on a separated thread. It requires that the class has a property
    called ``_threads`` which is a list and holds all the running threads.
    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        logger = get_logger(name=__name__)
        logger.info('Starting new thread for {}'.format(func.__name__))
        args[0]._threads.append([func.__name__, Thread(target=func, args=args, kwargs=kwargs)])
        args[0]._threads[-1][1].start()
        logger.debug('In total there are {} threads'.format(len(args[0]._threads)))

    return func_wrapper


def make_async_process(func):
    """ Simple decorator to start a method as a separated process. It requires that the class has a property
    called ``_processes`` which is a list and holds all the running processes.
    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        logger = get_logger(name=__name__)
        logger.info('Starting a new thread for {}'.format(func.__name__))
        args[0]._processes.append([func.__name__, Process(target=func, args=args, kwargs=kwargs)])
        args[0]._processes[-1][1].start()
        logger.debug('In total there are {} processes'.format(len(args[0]._threads)))

    return func_wrapper