#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

"""Base application framework."""

import logging
import sys

from .base_app import *

_logger = logging.getLogger(__name__)

init = DefaultManager.init
fini = DefaultManager.fini
onmain = DefaultManager.onmain
start = DefaultManager.start

@onmain
def _handle_exceptions(**kwargs):
    try:
        yield kwargs
    except SystemExit:
        raise
    except:
        _logger.error('Unhandled exception', exc_info=True)
        sys.exit(1)


from . import flag
from . import logs
