#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

from . import base_app as app
from .base_flag import *

argroup = DefaultManager.argroup

@app.DefaultManager.onmain
def _parse_flags(**kwargs):
    flags = DefaultManager.parse_args()
    args = kwargs.copy()
    args['flags'] = flags
    yield args
