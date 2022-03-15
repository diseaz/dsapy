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


class _globals:
    init = []
    fini = []
    onmain = []
    onwrapmain = []
    main = []


def init(func):
    _globals.init.append(func)


def fini(func):
    _globals.fini.append(func)


def onmain(func):
    _globals.onmain.append(
        contextlib.contextmanager(func)
    )


def onwrapmain(func):
    _globals.onwrapmain.append(func)


def main(**kwargs):
    '''Declares a function to be a main function.

    There can be any number of main functions declared: 0, 1 or more.  It's
    up to 'onwrapmain', 'init' and 'onmain' handlers to select one of
    several or provide a replacement.  Selection may be based e.g. on
    command line flags.
    '''
    def main_wrapper(main_func):
        kw = kwargs.copy()
        kw['main_func'] = main_func
        for handler in _globals.onwrapmain:
            kw = handler(**kw)
        main_func = kw['main_func']
        _globals.main.append(main_func)
        return main_func
    return main_wrapper


def get_commands():
    return _globals.main


def start(main_func=None, **kwargs):
    with contextlib.ExitStack() as estack:
        for f in _globals.fini:
            estack.callback(f)

        if main_func is not None:
            kwargs['main_func'] = main_func

        for f in _globals.init:
            new_kwargs = f(**kwargs)
            if new_kwargs is not None:
                kwargs = new_kwargs

        for w in _globals.onmain:
            kwargs = estack.enter_context(w(**kwargs))

        main_func = kwargs.pop('main_func', None)
        if main_func is not None:
            main_func(**kwargs)
