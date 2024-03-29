#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

"""Base application framework."""

from typing import Any

import logging
import sys

from .base_app import \
    Error, BrokenWrapperError, \
    init, fini, onmain, onwrapmain, main, start, \
    get_commands, \
    KwArgsGenerator  # noqa: F401
from . import base_flag  # noqa: F401

_logger = logging.getLogger(__name__)


@onmain
def _handle_exceptions(**kwargs):
    try:
        yield kwargs
    except SystemExit:
        raise
    except:  # noqa: E722
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

    flags: Any

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)

    @classmethod
    def add_arguments(cls, argparser):
        return

    def main(self):
        return
