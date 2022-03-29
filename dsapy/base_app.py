#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

"""Base application framework."""

from typing import Any, Dict, Callable, Generator, Optional, ContextManager, List

import contextlib


class Error(Exception):
    """Base class for errors in the module."""


class BrokenWrapperError(Error):
    """Something wrong with wrapper for main."""


KwArgs = Dict[str, Any]
KwArgsGenerator = Generator[KwArgs, None, None]
InitFunc = Callable[..., Optional[KwArgs]]
FiniFunc = Callable[..., None]
OnMainFunc = Callable[..., KwArgsGenerator]
OnMainHandler = Callable[..., ContextManager[KwArgs]]
OnWrapMainFunc = Callable[..., KwArgs]
MainFunc = Callable[..., Any]


class _globals:
    init: List[InitFunc] = []
    fini: List[FiniFunc] = []
    onmain: List[OnMainHandler] = []
    onwrapmain: List[OnWrapMainFunc] = []
    main: List[MainFunc] = []


def init(func: InitFunc) -> None:
    _globals.init.append(func)


def fini(func: FiniFunc):
    _globals.fini.append(func)


def onmain(func: OnMainFunc):
    _globals.onmain.append(
        contextlib.contextmanager(func)
    )


def onwrapmain(func: OnWrapMainFunc):
    _globals.onwrapmain.append(func)


def main(**kwargs: Any):
    '''Declares a function to be a main function.

    There can be any number of main functions declared: 0, 1 or more.  It's
    up to 'onwrapmain', 'init' and 'onmain' handlers to select one of
    several or provide a replacement.  Selection may be based e.g. on
    command line flags.
    '''
    def main_wrapper(main_func: MainFunc):
        kw = kwargs
        kw['main_func'] = main_func
        for handler in _globals.onwrapmain:
            kw = handler(**kw)
        main_func = kw['main_func']
        _globals.main.append(main_func)
        return main_func
    return main_wrapper


def get_commands() -> List[MainFunc]:
    return _globals.main


def start(main_func: MainFunc = None, **kwargs: Any) -> None:
    with contextlib.ExitStack() as estack:
        for fini_f in _globals.fini:
            estack.callback(fini_f)

        if main_func is not None:
            kwargs['main_func'] = main_func

        for init_f in _globals.init:
            new_kwargs = init_f(**kwargs)
            if new_kwargs is not None:
                kwargs = new_kwargs

        for w in _globals.onmain:
            kwargs = estack.enter_context(w(**kwargs))

        main_func = kwargs.pop('main_func', None)
        if main_func is not None:
            main_func(**kwargs)
