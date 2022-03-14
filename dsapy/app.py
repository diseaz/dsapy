#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

"""Base application framework."""

import logging
import sys

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

        parser_kwargs = getattr(new_cls, 'parser_kwargs', {}).copy()
        if new_cls.__doc__:
            parser_kwargs['description'] = new_cls.__doc__
        if hasattr(new_cls, 'add_arguments'):
            parser_kwargs['add_arguments'] = new_cls.add_arguments

        def main_func(**kwargs):
            return new_cls(**kwargs).main()

        main_func.name = getattr(new_cls, 'name', name)
        main(**parser_kwargs)(main_func)

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
