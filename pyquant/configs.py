#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

import os
import json
import logging

from pyquant.xdict import Dict

_defaultconfig = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config-default.json')
_overrideconfig = './config.json'

def _load(file):
    with open(file, 'r') as fp:
        return json.load(fp, object_hook=_todict)

def _todict(d):
    return Dict(**d)

def _merge(src, dest):
    '''
    deep merge two dicts.

    >>> a = Dict(first=Dict(a=11, b=22), second=222)
    >>> b = Dict(first=Dict(a=99, c=88), third=333)
    >>> _merge(a, b)
    >>> print(b.second)
    222
    >>> print(b.first.a)
    11
    '''
    for key, value in src.items():
        if isinstance(value, dict):
            # get node or create one
            node = dest.setdefault(key, {})
            _merge(value, node)
        else:
            dest[key] = value

def _loadconfig():
    cfg = _load(_defaultconfig)
    if os.path.isfile(_overrideconfig):
        logging.info('Load override config %s...' % _overrideconfig)
        override = _load(_overrideconfig)
        _merge(override, cfg)
    return cfg

config = _loadconfig()

if __name__=='__main__':
    import doctest
    doctest.testmod()
