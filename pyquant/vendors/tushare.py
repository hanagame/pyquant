
'''
tushare data vendor for stock A.

install tushare >= 0.5.9:

$ pip install tushare
'''

__author__ = 'Michael Liao'

import logging
import tushare

from pyquant import configs
from pyquant.models import Vendor

NAME = 'tushare'

def init():
    vs = Vendor.findAll(where='name=?', args=(NAME,))
    if len(vs)==0:
        v = Vendor(name=NAME, url='http://tushare.org')
        v.save()
        logging.info('Init tushare ok.')

def update(since=None):
    pass
