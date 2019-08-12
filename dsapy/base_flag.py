#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

import argparse

from . import base_app as app
from . import base_logs as logs


class Manager(object):
    def __init__(self):
        self.main_params = {}
        self.argroups = []

    def main(self, description=None, prog=None, usage=None, epilog=None):
        def wrapper(func):
            self.main_params = {
                'kwargs': {
                    'description': description,
                    'prog': prog,
                    'usage': usage,
                    'epilog': epilog,
                },
                'func': func,
            }
            return func
        return wrapper

    def argroup(self, title, *args, **kwargs):
        def wrapper(func):
            pargs = (title,) + args
            self.argroups.append({'args': pargs, 'kwargs': kwargs, 'func': func})
            return func
        return wrapper

    def populate_argparser(self, argparser):
        for g in self.argroups:
            argroup = argparser.add_argument_group(*g['args'], **g['kwargs'])
            g['func'](argroup)

    def parse_args(self, *args, **kwargs):
        argparser = argparse.ArgumentParser(
            formatter_class=DefaultFormatter,
            fromfile_prefix_chars='@',
            **self.main_params
        )
        self.populate_argparser(argparser)
        return argparser.parse_args(*args, **kwargs)


class DefaultFormatter(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
):
    pass


DefaultManager = Manager()
