#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

"""Base application framework."""

import logging
import sys
from typing import *

from .base_app import *
from . import base_flag

_logger = logging.getLogger(__name__)


@onmain
def _handle_exceptions(**kwargs):
    try:
        yield kwargs
    except SystemExit:
        raise
    except:
        _logger.error('Unhandled exception', exc_info=True)
        sys.exit(1)


class _commandMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        skip = kwds.pop('skip', False)
        new_cls = super().__new__(cls, name, bases, namespace, **kwds)

        if skip:
            return new_cls

        def main_func(**kwargs):
            return new_cls(**kwargs).main()

        add_arguments = getattr(new_cls, 'add_arguments', None)
        if add_arguments:
            main_func.add_arguments = add_arguments

        main(
            name=getattr(new_cls, 'name', name),
            help=getattr(new_cls, 'help', None),
            description=getattr(new_cls, 'description', None) or new_cls.__doc__,
        )(main_func)

        return new_cls


class Command(metaclass=_commandMeta, skip=True):
    """Base class for subcommand."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def add_arguments(cls, argparser):
        return

    def main(self):
        return
