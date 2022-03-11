#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

"""Base application framework."""

import collections
import contextlib
import sys


class Error(Exception):
    """Base class for errors in the module."""


class BrokenWrapperError(Error):
    """Something wrong with wrapper for main."""


class Manager(object):
    def __init__(self):
        self.inits = []
        self.finis = []
        self.wrappers = []
        self.onwrap = []

    def init(self, func):
        self.inits.append(func)

    def fini(self, func):
        self.finis.append(func)

    def onmain(self, func):
        self.wrappers.append(
            contextlib.contextmanager(func)
        )

    def onwrapmain(self, handler_func=None):
        self.onwrap.append(handler_func)
        return handler_func

    def main(self, **kwargs):
        def main_wrapper(main_func):
            for handler in self.onwrap:
                main_func = handler(main_func, **kwargs)
            return main_func
        return main_wrapper

    def start(self, main_func=None):
        with contextlib.ExitStack() as estack:
            # cf = inspect.getouterframes(inspect.currentframe())[1]

            kwargs = {}
            if main_func is not None:
                kwargs['main_func'] = main_func
            for w in self.wrappers:
                kwargs = estack.enter_context(w(**kwargs))

            for f in self.inits:
                f()

            main_func = kwargs.pop('main_func', None)
            if main_func is not None:
                main_func(**kwargs)

            for f in self.finis[::-1]:
                f()


DefaultManager = Manager()
