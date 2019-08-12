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

    def init(self, func):
        self.inits.append(func)

    def fini(self, func):
        self.finis.append(func)

    def onmain(self, func):
        self.wrappers.append(
            contextlib.contextmanager(func)
        )

    def start(self, main_func):
        with contextlib.ExitStack() as estack:
            kwargs = {}
            for w in self.wrappers:
                kwargs = estack.enter_context(w(**kwargs))

            for f in self.inits:
                f()

            main_func(**kwargs)

            for f in self.finis[::-1]:
                f()


DefaultManager = Manager()
