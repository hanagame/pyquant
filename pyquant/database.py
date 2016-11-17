#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'database support'

__author__ = 'Michael Liao'

import logging;logging.basicConfig(level=logging.INFO)
import functools
import threading
import MySQLdb as mysql

from pyquant.configs import config
from pyquant.xdict import Dict

def _connect():
    '''
    make connection to mysql
    '''
    params = dict(**config.db)
    params['use_unicode'] = True
    params['charset'] = 'utf8'
    params['autocommit'] = False
    return mysql.connect(**params)

# tx support:

_tx_local = threading.local()

def transactional(func):
    '''
    Decorator for create new transaction or join current transaction.
    '''
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        conn = getattr(_tx_local, 'connection', None)
        should_close = False
        try:
            if conn is None:
                # open new connection:
                conn = _connect()
                _tx_local.connection = conn
                should_close = True
            r = func(*args, **kw)
            if should_close:
                conn.commit()
            return r
        except BaseException:
            if should_close:
                conn.rollback()
            raise
        finally:
            if should_close:
                _tx_local.connection = None
                conn.close()
    return _wrapper

@transactional
def select(sql, args=(), size=None):
    '''
    execute select SQL and return list results.
    '''
    global _tx_local
    logging.info('SELECT: %s, ARGS: %s' % (sql, args))
    cursor = None
    try:
        cursor = _tx_local.connection.cursor(mysql.cursors.DictCursor)
        cursor.execute(sql.replace('?', '%s'), args)
        rs = cursor.fetchmany(size) if size else cursor.fetchall()
        return [Dict(**r) for r in rs]
    finally:
        if cursor:
            cursor.close()

@transactional
def execute(sql, args=()):
    global _tx_local
    logging.info('EXEC: %s, ARGS: %s' % (sql, args))
    cursor = None
    try:
        cursor = _tx_local.connection.cursor(mysql.cursors.DictCursor)
        cursor.execute(sql.replace('?', '%s'), args)
        return cursor.rowcount
    finally:
        if cursor:
            cursor.close()
