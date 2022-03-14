#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import logging
from dsapy import app


_logger = logging.getLogger(__name__)


def _options1(parser):
    parser.add_argument(
        '--who',
        default='world',
        help='Who to greet',
    )


def _options2(parser):
    parser.add_argument(
        '-t', '--target',
        default='world',
        help='Say hello to who?',
    )


@app.main(add_arguments=_options1)
def greet(flags, **kwargs):
    """Greets someone."""
    print('Greetings, {}!'.format(flags.who))


@app.main(
    add_arguments=_options2,
    description='Says hello to anybody.\nAnybody is "world" by default.',
    help='Helloes someone.',
)
def hello(flags, **kwargs):
    """Says hello."""
    print('Hello, {}!'.format(flags.target))


class Say(app.Command):
    """Says text."""

    name='say'

    @classmethod
    def add_arguments(self, argparser):
        argparser.add_argument(
            'text',
            default='',
            nargs='?',
            help='What to say',
        )

    def main(self):
        """Main function."""
        print(self.flags.text)


if __name__ == '__main__':
    app.start()
