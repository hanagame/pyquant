
'''
tushare data vendor for stock A.

install tushare >= 0.5.9:

$ pip install tushare
'''

__author__ = 'Michael Liao'

import logging
import tushare

from datetime import date

from pyquant import configs
from pyquant.models import Vendor

class DataVendor(object):

    def __init__(self):
        self.name = 'tushare'
        self.since = '2001-01-01'
        vs = Vendor.findAll(where='name=?', args=(self.name,))
        if len(vs)==0:
            v = Vendor(name=self.name, url='http://tushare.org')
            v.save()
        logging.info('Init tushare ok.')

    def update(self):
        '''
        Called by data-fetch thread.
        '''
        pass

    def query(self, symbol, tickType, fromTime, endTime):
        pass


