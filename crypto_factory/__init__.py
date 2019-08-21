# -*- coding: utf-8 -*-
"""Crypto-Factory

Main purpose of this library is to provide a common interface to application
for cryptographic tasks.
"""

# TODO: Update docstrings.
# TODO: Finish writing documentation
# TODO: Create HOWTOs
# TODO: Import providers only if required pkg(s) present
# TODO: {Last} Clean up code !!!


import logging
from .interface import CryptoFactory
from . import templates
from . import providers
from . import utils
from . import exceptions


__all__ = [
    'CryptoFactory',
    'templates',
    'providers',
    'utils',
    'exceptions',
]

name = "crypto_factory"

__title__ = "Crypto-Factory"
__summary__ = "Standardize cryptographic tasks in your application."
__uri__ = "https://github.com/LuckyDams/Crypto-Factory"

__version__ = "0.0.9"
__version_info__ = tuple(int(x) for x in __version__.split('.'))
__build__ = "20190620"

__author__ = "LuckyDams"
__email__ = "LuckyDams@gmail.org"

__license__ = "MIT"
__copyright__ = "Copyright 2019 {}".format(__author__)

# Create library logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
