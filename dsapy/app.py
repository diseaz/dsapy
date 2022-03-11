#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

"""Base application framework."""

import logging
import sys

from . import base_app

_logger = logging.getLogger(__name__)

init = base_app.DefaultManager.init
fini = base_app.DefaultManager.fini
onmain = base_app.DefaultManager.onmain
onwrapmain = base_app.DefaultManager.onwrapmain
start = base_app.DefaultManager.start
main = base_app.DefaultManager.main

Error = base_app.Error
BrokenWrapperError = base_app.BrokenWrapperError


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

        if not skip:
            parser_kwargs = {
                'description': new_cls.__doc__,
                'add_arguments': getattr(new_cls, 'add_arguments', None),
            }
            parser_kwargs.update(getattr(new_cls, 'parser_kwargs', {}))

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
