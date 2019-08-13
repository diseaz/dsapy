#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

from . import base_app
from . import base_flag

argroup = base_flag.DefaultManager.argroup
argparser = base_flag.DefaultManager.argparser


base_app.DefaultManager.onmain(base_flag.DefaultManager.parse_flags)
