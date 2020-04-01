#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

from logging import *
from . import base_app as app
from . import base_logs
from . import base_flag as flag


def _level_key(lvl):
    while True:
        level_record = base_logs.Levels[lvl]
        if 'alias' in level_record:
            lvl = level_record['alias']
            continue
        return (-level_record['level'], len(level_record['format']))


@flag.DefaultManager.argroup('Logging')
def _flags(argroup):
    levels = list(base_logs.Levels.keys())
    levels.sort(key=_level_key)

    argroup.add_argument(
        '--log-level',
        choices=levels,
        default=base_logs._getDefaultLevelName(),
        metavar='LEVEL',
        help='Logging level. Supported values: {0}'.format(', '.join(levels)),
    )
    argroup.add_argument(
        '--log-format',
        default=None,
        metavar='FORMAT',
        help='Log record format',
    )
    argroup.add_argument(
        '--log-datefmt',
        default=None,
        metavar='DATEFMT',
        help='Datetime format for logging',
    )


@app.DefaultManager.onmain
def _init(**kwargs):
    root_logger = getLogger()
    root_logger.handlers = []

    flags = kwargs['flags']
    basic_args = base_logs.Levels[flags.log_level].copy()
    if flags.log_format is not None:
        basic_args['format'] = flags.log_format
    if flags.log_datefmt is not None:
        basic_args['datefmt'] = flags.log_datefmt
    basicConfig(**basic_args)

    yield kwargs


def overrideEnvLevel(level):
    base_logs.OverrideEnvLevel = level
