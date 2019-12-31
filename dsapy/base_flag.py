#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

import argparse
import inspect
import logging
import sys

_logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for exceptions in the module."""


class MainFuncConflictError(Error):
    """Main functions with conflicting names."""


class Manager(object):
    def __init__(self):
        self.argparsers = []
        self.subcommands = []

    def main(self, add_arguments=None, **parser_kwargs):
        def wrapper(func):
            self.subcommands.append(self.wrap_main_func(func, add_arguments, parser_kwargs))
            return func
        return wrapper

    def argroup(self, title, *args, **kwargs):
        def wrapper(func):
            def argparser(parser):
                pargs = (title,) + args
                argroup = parser.add_argument_group(*pargs, **kwargs)
                return func(argroup)
            self.argparsers.append(argparser)
            return func
        return wrapper

    def argparser(self, func):
        self.argparsers.append(func)
        return func

    def wrap_main_func(self, func, add_arguments=None, parser_kwargs={}):
        if func is None:
            return None
        doc = parser_kwargs.get('description') or func.__doc__ or getattr(inspect.getmodule(func), '__doc__')
        help = None if doc is None else doc.split('\n', 1)[0]
        kwargs = {
            'description': doc,
            'help': help,
        }
        kwargs.update(parser_kwargs)
        func.parser_kwargs = kwargs
        func.add_arguments = add_arguments
        return func

    def populate_single_command_argparser(self, argparser, main_func):
        for g in self.argparsers:
            g(argparser)
        add_arguments = getattr(main_func, 'add_arguments', None)
        if add_arguments != None:
            add_arguments(argparser)
        argparser.set_defaults(main_func=main_func)

    def populate_multi_command_argparser(self, argparser, commands):
        subparsers = argparser.add_subparsers(title='subcommands')
        for cmd in commands:
            kwargs = cmd.parser_kwargs.copy()
            n = kwargs.pop('name', getattr(cmd, 'name', getattr(cmd, '__name__', None)))
            parser = subparsers.add_parser(name=n, **kwargs)
            self.populate_single_command_argparser(parser, cmd)

    def detect_mode(self, main_func=None, force_subcommands=False):
        if main_func is not None:
            return [main_func], False

        if not self.subcommands:
            raise MainFuncConflictError('No main functions registered')

        seen = {}
        mains = []
        for s in self.subcommands:
            n = getattr(s, 'name', getattr(s, '__name__', None))
            if n is None:
                mains.append(s)
            elif n in seen:
                raise MainFuncConflictError('Subcommand name conflict: name={!r}'.format(n))
            else:
                seen[n] = s

        if len(mains) > 1:
            raise MainFuncConflictError('Too many unnamed mains')
        elif len(mains) == 1:
            if force_subcommands:
                raise MainFuncConflictError('Unnamed main with force_subcommands')
            elif len(self.subcommands) > 1:
                raise MainFuncConflictError('Unnamed main with more than one subcommand')

        multicommand = (len(self.subcommands) > 1) or force_subcommands
        return self.subcommands, multicommand

    def parse_single_command_args(self, main_func, **kwargs):
        parser_kwargs = main_func.parser_kwargs.copy()
        parser_kwargs.update(kwargs)
        parser_kwargs.pop('help', None)
        argparser = argparse.ArgumentParser(
            formatter_class=DefaultFormatter,
            fromfile_prefix_chars='@',
            **parser_kwargs
        )
        self.populate_single_command_argparser(argparser, main_func)
        flags = argparser.parse_args()
        if not hasattr(flags, 'main_func'):
            argparser.error('No main function')
        return flags

    def parse_multi_command_args(self, commands, **kwargs):
        argparser = argparse.ArgumentParser(
            formatter_class=DefaultFormatter,
            fromfile_prefix_chars='@',
            **kwargs
        )
        self.populate_multi_command_argparser(argparser, commands)
        flags = argparser.parse_args()
        if not hasattr(flags, 'main_func'):
            argparser.error('Subcommand is required')
        return flags

    def parse_args(self, main_func=None, force_subcommands=False, **kwargs):
        commands, multicommand = self.detect_mode(main_func=main_func, force_subcommands=force_subcommands)
        if multicommand:
            return self.parse_multi_command_args(commands, **kwargs)
        else:
            return self.parse_single_command_args(commands[0], **kwargs)

    def parse_flags(self, main_func=None, force_subcommands=False, **kwargs):
        main_func = self.wrap_main_func(main_func, parser_kwargs=kwargs)
        flags = self.parse_args(main_func=main_func, force_subcommands=force_subcommands, **kwargs)
        kwargs['flags'] = flags
        kwargs['main_func'] = getattr(flags, 'main_func', None)
        yield kwargs


class DefaultFormatter(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
):
    pass


DefaultManager = Manager()
