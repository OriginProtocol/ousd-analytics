import os
import logging

parent_logger = logging.getLogger()
parent_logger.setLevel(os.environ.get('LOG_LEVEL', logging.INFO))


def get_logger(name):
    """ Get a child logger with given name """
    return parent_logger.getChild(name)
