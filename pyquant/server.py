#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'web server by flask'

__author__ = 'Michael Liao'

import os

from flask import Flask, render_template

app = Flask('pyquant', template_folder=os.path.join(os.path.dirname(__file__) , 'templates'))

@app.route('/')
def index():
    return 'It works!'

@app.route('/btc')
def btc():
    return render_template('btc.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1818)
