#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

from dsapy import app


def _options(parser):
    parser.add_argument(
        '--who',
        default='world',
        help='Who to greet',
    )


@app.main(add_arguments=_options)
def main(flags, **kwargs):
    """Simplest helloworld example
    """
    print('Hello, {}!'.format(flags.who))


if __name__ == '__main__':
    app.start()
