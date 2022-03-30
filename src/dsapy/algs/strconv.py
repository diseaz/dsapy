#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

from typing import Dict, Optional

_bool_values: Dict[str, bool] = {
    'true': True,
    't': True,
    'yes': True,
    'y': True,
    '1': True,

    'false': False,
    'f': False,
    'no': False,
    'n': False,
    '0': False,
}


def parse_bool(s: Optional[str], default: bool = False) -> bool:
    if not s:
        return default
    return _bool_values.get(s.lower(), default)
