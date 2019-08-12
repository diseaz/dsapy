#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import os

from dsapy import app
from dsapy import flag


@flag.argroup('Options')
def _options(argroup):
    argroup.add_argument(
        '--who',
        default='world',
        help='Who to greet',
    )


@flag.main()
def main(flags, **kwargs):
    """Simplest helloworld example
    """
    print('Hello, {}!'.format(flags.who))


if __name__ == '__main__':
    app.start(main)
