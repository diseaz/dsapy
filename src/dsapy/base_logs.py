#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

from typing import Any, Dict

import logging
import os


_default_format_long = '%(asctime)s %(levelname)s %(name)s@%(lineno)d: %(message)s'
_default_format_short = '%(asctime)s %(message)s'
_default_format_tiny = '%(message)s'
_default_datefmt = '%Y-%m-%d %H:%M:%S'

Levels: Dict[str, Dict[str, Any]] = {
    'error': {
        'level': logging.ERROR,
        'datefmt': _default_datefmt,
        'format': _default_format_tiny,
    },
    'warning': {
        'alias': 'warn',
    },
    'warn': {
        'level': logging.WARNING,
        'datefmt': _default_datefmt,
        'format': _default_format_tiny,
    },
    'info': {
        'level': logging.INFO,
        'datefmt': _default_datefmt,
        'format': _default_format_tiny,
    },
    'normal': {
        'level': logging.INFO,
        'datefmt': _default_datefmt,
        'format': _default_format_short,
    },
    'verbose': {
        'level': logging.DEBUG,
        'datefmt': _default_datefmt,
        'format': _default_format_short,
    },
    'debug': {
        'level': logging.DEBUG,
        'datefmt': _default_datefmt,
        'format': _default_format_long,
    },
}

DefaultLevel = 'normal'
OverrideEnvLevel = None


def _getDefaultLevelName():
    envLogLevel = os.environ.get('DSAPY_LOG_LEVEL', None)
    log_level = (
        OverrideEnvLevel or envLogLevel or DefaultLevel
    ).lower()

    while True:
        if log_level not in Levels:
            log_level = DefaultLevel
        level_record = Levels[log_level]
        if 'alias' not in level_record:
            return log_level
        log_level = level_record['alias']


logging.basicConfig(**Levels[_getDefaultLevelName()])
