
'''
tushare data vendor for stock A.

install tushare >= 0.5.9:

$ pip install tushare
'''

__author__ = 'Michael Liao'

import logging
import tushare

from datetime import date

from pyquant.models import Vendor, Exchange, Symbol

def _createVendor():
    vs = Vendor.findAll(where='code=?', args=('tushare',))
    if len(vs)==0:
        logging.info('add vendor: tushare...')
        v = Vendor(code='tushare', name='Tushare', url='http://tushare.org')
        v.save()
        return v
    return vs[0]

def _createExchange(code, name):
    ex = Exchange.findAll(where='code=?', args=(code,))
    if len(ex)==0:
        logging.info('add exchange: %s...' % code)
        e = Exchange(code=code, name=name, currency='CNY', timezone='GMT+08:00')
        e.save()
        return e
    return ex[0]

class DataVendor(object):

    def __init__(self, **kw):
        self.name = 'tushare'
        self.since = '2001-01-01'
        self.vendor = _createVendor()
        self.sse = _createExchange('SSE', '上海证券交易所')
        self.sze = _createExchange('SZE', '深圳证券交易所')
        es = Exchange.findAll(where='code =?', args=('SSE', 'SZE'))

        logging.info('Init tushare ok.')

    def update(self):
        '''
        Called by background data-fetch-thread.
        '''
        logging.info('Update...')
        if self._need_refresh_index():
            logging.info('Refresh stock list...')
            self._update_index()

    def query(self, symbol, tickType, fromTime, endTime):
        pass

    def _need_refresh_index(self):
        if getattr(self, 'need_refresh_index', None):
            return False
        self.need_refresh_index = True
        return True

    def _update_index(self):
        ss = tushare.get_stock_basics()
        for code in ss.index:
            stock = dict(ss.ix[code])
            # todo: save stock...
