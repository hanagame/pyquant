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

app = Flask('pyquant', template_folder=os.path.join(os.path.dirname(__file__) , 'templates'))

@app.route('/')
def index():
    return 'It works!'

@app.route('/btc')
def btc():
    return render_template('btc.html')

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
            logging.warn(e)
            if n < 16:
                n = n * 2
        time.sleep(n)

if __name__ == '__main__':
    _start()
    app.run(host='127.0.0.1', port=1818)
