from functools import wraps

from experimentor.lib.log import get_logger

logger = get_logger(__name__)


def not_implemented(func):
    @wraps(func)
    def func_wrapper(cls, *args, **kwargs):
        logger.warning(f'{cls}.{func.__name__} Not Implemented')
        return func(cls, *args, **kwargs)
    return func_wrapper
