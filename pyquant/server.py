#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'web server by flask'

__author__ = 'Michael Liao'

import os
import time
import logging
import threading

logging.basicConfig(format='%(levelname)s %(threadName)s %(asctime)s: %(message)s', level=logging.INFO)

from flask import Flask, render_template

from pyquant import configs
from pyquant.models import Exchange, Symbol, K1DPrice

app = Flask('pyquant', template_folder=os.path.join(os.path.dirname(__file__) , 'templates'))

@app.route('/')
def index():
    return 'It works!'

@app.route('/symbols')
def symbols():
    symbols = Symbol.findAll(orderby='code')
    return render_template('symbols.html', dict(symbols=symbols))

@app.route('/k1d')
    symbols = Symbol.findAll(where='code=?', args=('600036',))
    symbol = symbols[0]
    kdata = K1DPrice.findAll(where='symbol_id=?', args=(symbol.id,), orderby='price_date desc', limit=365)
    return render_template('btc.html', dict(kdata: kdata))

def _start():
    _startfetchthreads()

def _startfetchthreads():
    vendorinstances = []
    for vendor, initkw in configs.config.vendors.items():
        mod = __import__('pyquant.vendors.%s' % vendor, fromlist=vendor)
        vendorinstances.append((vendor, mod.DataVendor(**initkw)))
    for name, v in vendorinstances:
        _startfetchthread(name, v)

def _startfetchthread(name, vendor):
    t = threading.Thread(target=_startvendor, name=name, args=(vendor,))
    t.start()

def _startvendor(vendor):
    n = 1
    while True:
        try:
            vendor.update()
            n = 1
        except Exception as e:
            logging.exception('update failed.')
            if n < 16:
                n = n * 2
        time.sleep(n)

if __name__ == '__main__':
    _start()
    app.run(host='127.0.0.1', port=1818)
