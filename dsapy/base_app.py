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
        self.__init = []
        self.__fini = []
        self.__onmain = []
        self.__onwrapmain = []

    def init(self, func):
        self.__init.append(func)

    def fini(self, func):
        self.__fini.append(func)

    def onmain(self, func):
        self.__onmain.append(
            contextlib.contextmanager(func)
        )

    def onwrapmain(self, handler_func):
        self.__onwrapmain.append(handler_func)

    def main(self, **kwargs):
        def main_wrapper(main_func):
            for handler in self.__onwrapmain:
                main_func = handler(main_func, **kwargs)
            return main_func
        return main_wrapper

    def start(self, main_func=None):
        with contextlib.ExitStack() as estack:
            for f in self.__fini:
                estack.callback(f)

            kwargs = {}
            if main_func is not None:
                kwargs['main_func'] = main_func

            for f in self.__init:
                new_kwargs = f(**kwargs)
                if new_kwargs is not None:
                    kwargs = new_kwargs

            for w in self.__onmain:
                kwargs = estack.enter_context(w(**kwargs))

            main_func = kwargs.pop('main_func', None)
            if main_func is not None:
                main_func(**kwargs)


DefaultManager = Manager()
