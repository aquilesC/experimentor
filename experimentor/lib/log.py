# -*- coding: utf-8 -*-
"""
    nanoparticle_tracking.util.log.py
    =================================

    Adding log capacities to PyNTA


    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: AGPLv3, see LICENSE for more details
"""
import logging, multiprocessing


DEFAULT_FMT = "[%(levelname)8s] %(asctime)s %(name)s: %(message)s"


def get_logger(name='pynta', level=logging.INFO):
    logger = multiprocessing.get_logger()
    logger.setLevel(level)
    return logger


EXPERIMENTOR_LOGGER = get_logger()


def log_to_screen(level=logging.INFO, fmt=None):
    fmt = fmt or DEFAULT_FMT
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    EXPERIMENTOR_LOGGER.addHandler(handler)
    return handler


def log_to_file(filename, level=logging.INFO, fmt=None):
    fmt = fmt or DEFAULT_FMT
    handler = logging.FileHandler(filename)
    handler.setLevel(level)
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    EXPERIMENTOR_LOGGER.addHandler(handler)
    return handler
