#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

import argparse
import inspect
import logging
import sys

from . import base_app as app

_logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for exceptions in the module."""


class MainFuncConflictError(Error):
    """Main functions with conflicting names."""


class _globals:
    argparsers = []


def argroup(title, description=None):
    def argroup_wrapper(func):
        def argparser(parser):
            argroup = parser.add_argument_group(title, description)
            return func(argroup)
        _globals.argparsers.append(argparser)
        return func
    return argroup_wrapper


def argparser(func):
    self.argparsers.append(func)
    return func


_known_kwargs = [
    'description',
    'help',
    'add_arguments',
    'parser_kwargs',
    'subparser_kwargs',
]

@app.onwrapmain
def _set_flag_properties(**kwargs):
    main_func = kwargs['main_func']
    for n in _known_kwargs:
        if n in kwargs:
            setattr(main_func, n, kwargs[n])
    return kwargs


@app.init
def _init_parse_flags(**kwargs):
    '''Parses flags in initialization sequence.

    Args:

        - main_func: explicit main function provided to `app.start` or
          preselected by some earlier init function in the sequence.

        - multicommand: if there was only one command registered with
          `app.main`, act as if there is multiple commands.
    '''
    commands, multicommand, kwargs = _detect_mode(**kwargs)
    if multicommand:
        flags = _parse_multi_command_args(commands, **kwargs)
    else:
        flags = _parse_single_command_args(commands[0], **kwargs)
    kwargs['flags'] = flags
    if hasattr(flags, 'main_func'):
        kwargs['main_func'] = flags.main_func
    return kwargs


def _detect_mode(main_func=None, multicommand=False, **kwargs):
    if main_func is not None:
        return [main_func], False, kwargs

    subcommands = app.get_commands()
    if not subcommands:
        raise MainFuncConflictError('No main functions registered')

    seen = {}
    mains = []
    for s in subcommands:
        name = _command_name(s)
        if name is None:
            mains.append(s)
        elif name in seen:
            raise MainFuncConflictError('Subcommand name conflict: name={!r}'.format(name))
        else:
            seen[name] = s

    if len(mains) > 1:
        raise MainFuncConflictError('Too many unnamed mains')
    elif len(mains) == 1:
        if multicommand:
            raise MainFuncConflictError('Unnamed main with multicommand')
        elif len(subcommands) > 1:
            raise MainFuncConflictError('Unnamed main with more than one subcommand')

    multicommand = (len(subcommands) > 1) or multicommand
    return subcommands, multicommand, kwargs


def _command_name(cmd):
    return getattr(cmd, 'name', None) or getattr(cmd, '__name__', None)


def _command_kwargs(cmd):
    kwargs = {}
    description = getattr(cmd, 'description', None) or cmd.__doc__ or getattr(inspect.getmodule(cmd), '__doc__', None)
    if description:
        kwargs['description'] = description
    help = getattr(cmd, 'help', None) or (None if description is None else description.split('\n', 1)[0])
    if help:
        kwargs['help'] = help
    return kwargs


def _parse_single_command_args(main_func, **kwargs):
    parser_kwargs = _command_kwargs(main_func)
    if 'parser_kwargs' in kwargs:
        parser_kwargs.update(kwargs['parser_kwargs'])
    if hasattr(main_func, 'parser_kwargs'):
        parser_kwargs.update(main_func.parser_kwargs)
    argparser = argparse.ArgumentParser(
        formatter_class=DefaultFormatter,
        fromfile_prefix_chars='@',
        **parser_kwargs
    )
    _populate_single_command_argparser(argparser, main_func)
    flags = argparser.parse_args()
    if not hasattr(flags, 'main_func'):
        argparser.error('No main function')
    return flags


def _populate_single_command_argparser(argparser, main_func):
    for g in _globals.argparsers:
        g(argparser)
    if hasattr(main_func, 'add_arguments'):
        main_func.add_arguments(argparser)
    argparser.set_defaults(main_func=main_func)


def _parse_multi_command_args(commands, **kwargs):
    parser_kwargs = getattr(kwargs, 'parser_kwargs', {})
    argparser = argparse.ArgumentParser(
        formatter_class=DefaultFormatter,
        fromfile_prefix_chars='@',
        **parser_kwargs
    )
    subparser_kwargs = getattr(kwargs, 'subparser_kwargs', {})
    _populate_multi_command_argparser(argparser, commands, subparser_kwargs)
    flags = argparser.parse_args()
    if not hasattr(flags, 'main_func'):
        argparser.error('Subcommand is required')
    return flags


def _populate_multi_command_argparser(argparser, commands, subparser_kwargs):
    subparsers = argparser.add_subparsers(title='subcommands')
    for cmd in commands:
        kwargs = _command_kwargs(cmd)
        kwargs.update(subparser_kwargs)
        if hasattr(cmd, 'parser_kwargs'):
            kwargs.update(cmd.parser_kwargs)
        parser = subparsers.add_parser(
            name=_command_name(cmd),
            formatter_class=DefaultFormatter,
            fromfile_prefix_chars='@',
            **kwargs,
        )
        _populate_single_command_argparser(parser, cmd)


class DefaultFormatter(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
):
    pass
