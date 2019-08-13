#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import logging
from dsapy import app

_logger = logging.getLogger(__name__)


def _options(parser):
    parser.add_argument(
        '--who',
        default='world',
        help='Who to greet',
    )


@app.main(add_arguments=_options)
def greet(flags, **kwargs):
    """Greets someone."""
    print('Greetings, {}!'.format(flags.who))


@app.main(add_arguments=_options)
def hello(flags, **kwargs):
    """Says hello."""
    print('Hello, {}!'.format(flags.who))


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
