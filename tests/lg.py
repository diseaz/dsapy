#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import logging

from dsapy import app
from dsapy import flag
from dsapy import logs


_logger = logging.getLogger(__name__)


@flag.argparser
def _options(parser):
    parser.add_argument(
        '--who',
        default='world',
        help='Who to greet',
    )


@app.main()
def main(flags, **kwargs):
    """Simplest helloworld example
    """
    _logger.debug('debug')
    _logger.info('info')
    _logger.warning('warn')
    _logger.error('error')


if __name__ == '__main__':
    logs.overrideEnvLevel('info')
    app.start()
