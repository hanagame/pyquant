
'''
tushare data vendor for stock A.

install tushare >= 0.5.9:

$ pip install tushare
'''

__author__ = 'Michael Liao'

import time
import logging
import tushare

from datetime import date, datetime, timedelta

from pyquant.models import Vendor, Exchange, Symbol, K1DPrice
from pyquant.xdict import Dict

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
        logging.info('Init tushare ok.')

    def update(self):
        '''
        Called by background data-fetch-thread.
        '''
        logging.info('Update...')
        self._update_symbols()
        self._update_k1d('600036')

    def query(self, symbol, tickType, fromTime, endTime):
        pass

    def _update_k1d(self, code):
        # get last date since fetched:
        symbols = Symbol.findAll(where='code=?', args=(code,))
        symbol = symbols[0]
        lasts = K1DPrice.findAll(where='code=?', args=(code,), orderby='price_date desc', limit=1)
        if len(lasts) == 0:
            start = date(1991, 1, 1)
            logging.info('Fetch from beginning...')
        else:
            start = lasts[0].price_date + timedelta(days=1)
            logging.info('Fetch from %s...' % start)
        kd = tushare.get_k_data(code, start=str(start))
        saved = 0
        for i in kd.index:
            kdata = Dict(**kd.ix[i])
            d = datetime.strptime(kdata.date, '%Y-%m-%d').date()
            if d > start:
                kp = K1DPrice(vendor_id=self.vendor.id, \
                              symbol_id=symbol.id, \
                              code=code, \
                              price_date=kdata.date, \
                              open_price=kdata.open, \
                              high_price=kdata.high, \
                              low_price=kdata.low, \
                              close_price=kdata.close, \
                              adj_close_price=kdata.close, \
                              volume=kdata.volume)
                kp.save()
                saved = saved + 1
        logging.info('%s: saved %s.' % (code, saved))

    def _update_symbols(self):
        last_update = getattr(self, '_last_update_symbols', time.time())
        count = Symbol.findNumber('count(*)', where='exchange_id=?', args=(self.sse.id,))
        print(count)
        if (count > 10) and ((time.time() - last_update) < 28800):
            logging.info('No need update symbol list.')
            return
        logging.info('Update symbol list...')
        self._last_update_symbols = time.time()
        ss = tushare.get_stock_basics()
        updated = 0
        saved = 0
        for code in ss.index:
            stock = Dict(**ss.ix[code])
            symbols = Symbol.findAll(where='code=?', args=(code,))
            if len(symbols) > 0:
                symbol = symbols[0]
                symbol.name=stock.name
                symbol.industry=stock.industry
                symbol.area=stock.area
                symbol.outstanding=stock.outstanding
                symbol.totals=stock.totals
                symbol.update()
                updated = updated + 1
            else:
                symbol = Symbol(exchange_id=self._get_exchange_id(code), \
                                code=code, \
                                name=stock.name, \
                                currency='CNY', \
                                industry=stock.industry, \
                                area=stock.area, \
                                outstanding=stock.outstanding, \
                                total=stock.totals, \
                                is_index=False)
                symbol.save()
                saved = saved + 1
        logging.info('created %s, updated %s.' % (saved, updated))

    def _get_exchange_id(self, code):
        if code.startswith('0'):
            return self.sze.id
        if code.startswith('1'):
            return self.sze.id
        if code.startswith('3'):
            return self.sze.id
        return self.sse.id
