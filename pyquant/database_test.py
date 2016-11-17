#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

import time
import unittest

from pyquant.configs import config
from pyquant import database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        database.execute('drop table if exists t')
        database.execute('''
create table t (
    id bigint not null,
    name varchar(100) not null,
    created_at double not null,
    primary key (id)
)''')

    def test_query(self):
        rs = database.select('select 1 name from dual')
        self.assertIsNotNone(rs)
        self.assertEqual(len(rs), 1)
        self.assertEqual(rs[0].name, 1)

    def test_execute(self):
        id = 1892421
        # insert:
        n = database.execute('insert into t (id, name, created_at) values (?, ?, ?)', (id, 'Bob', time.time()))
        self.assertEqual(n, 1)
        # query:
        ts1 = database.select('select * from t where id=?', (id,))
        self.assertEqual(len(ts1), 1)
        self.assertEqual(ts1[0].name, 'Bob')
        # update:
        n = database.execute('update t set name=?, created_at=? where id=?', ('Tom', time.time(), id))
        self.assertEqual(n, 1)
        # query:
        ts2 = database.select('select * from t where id=?', (id,))
        self.assertEqual(len(ts2), 1)
        self.assertEqual(ts2[0].name, 'Tom')

    def test_tx(self):
        @database.transactional
        def run_in_tx():
            n = database.execute('insert into t (id, name, created_at) values (?, ?, ?)', (12345, 'Bob', time.time()))
            self.assertEqual(n, 1)
            raise Exception('will rollback')
        n = database.execute('insert into t (id, name, created_at) values (?, ?, ?)', (23456, 'Tom', time.time()))
        self.assertEqual(n, 1)
        try:
            run_in_tx()
            self.fail('not rollback')
        except AssertionError:
            raise
        except BaseException:
            pass
        rs = database.select('select * from t')
        self.assertEqual(len(rs), 1)
        self.assertEqual(rs[0].name, 'Tom')

if __name__ == '__main__':
    unittest.main()
