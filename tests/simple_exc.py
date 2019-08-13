#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import os

from dsapy import app
from dsapy import flag


@flag.argroup('Options')
def _options(argroup):
    argroup.add_argument(
        '--who',
        help='Who to greet',
    )


@app.main()
def main(flags, **kwargs):
    """Simple example that raises an unhandled exception in main.
    """
    greeting = 'Hello, ' + flags.who + '!'
    print(greeting)


if __name__ == '__main__':
    app.start(main)
