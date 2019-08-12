#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath('../..'))

from dsapy import app
from dsapy import flag


@flag.argroup('Options')
def _options(argroup):
    argroup.add_argument(
        '--who',
        help='Who to greet',
    )


def main(flags, **kwargs):
    greeting = 'Hello, ' + flags.who + '!'
    print(greeting)


if __name__ == '__main__':
    app.start(main)
