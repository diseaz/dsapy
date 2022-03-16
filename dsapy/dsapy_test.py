#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import contextlib
import os
import os.path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


_func_re = re.compile('<function (?:[^ ]*) at (?P<addr>0x[A-Fa-f0-9]*)>')


def _repl(m):
    all_text = m.group(0)
    all_span = m.span(0)
    all_len = all_span[1] - all_span[0]

    addr_span = m.span('addr')
    if addr_span != (-1, -1):
        addr_span = (addr_span[0] - all_span[0], addr_span[1] - all_span[1])
        return all_text[:addr_span[0]] + '0xADDRESS' + all_text[addr_span[1]:]

    return m.group(0)


def kw_as_str(kwargs):
    return _func_re.sub(_repl, repr(kwargs))
