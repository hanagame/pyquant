#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

import time
from datetime import date
from datetime import datetime
import unittest

from pyquant import database
from pyquant import model

class TestSimple(model.Model):
    name = model.StringField()
    gender = model.BooleanField()
    age = model.IntegerField(default=20)
    birth = model.DateField()
    current = model.DateTimeField()
    notify_at = model.FloatField(default=time.time)

class TestModel(unittest.TestCase):

    def setUp(self):
        database.execute('drop table if exists %s' % TestSimple.__table__)
        database.execute(TestSimple.__ddl__)

    def test_crud(self):
        now = datetime(2016, 11, 15, 1, 2, 3)
        s = TestSimple(name='Bob', gender=True, birth=date(2001, 1, 1), current=now)
        s.save()
        # query:
        q = TestSimple.find(s.id)
        self.assertIsNotNone(q)
        self.assertEqual(q.id, s.id)
        self.assertEqual(q.name, 'Bob')
        self.assertEqual(q.age, 20)
        self.assertEqual(q.birth, date(2001, 1, 1))
        self.assertEqual(q.current, now)
        self.assertAlmostEqual(q.notify_at, time.time(), delta=1.0)
        s.name = 'Tom'
        s.age = 33
        s.birth = date(1999, 9, 9)
        s.notify_at = 99099.99
        s.update()
        # query again:
        q2 = TestSimple.find(s.id)
        self.assertIsNotNone(q2)
        self.assertEqual(q2.id, s.id)
        self.assertEqual(q2.name, 'Tom')
        self.assertEqual(q2.age, 33)
        self.assertEqual(q2.birth, date(1999, 9, 9))
        self.assertAlmostEqual(q2.notify_at, 99099.99, delta=1.0)
        # remove:
        q2.remove()
        rs = TestSimple.findAll(orderby='id')
        self.assertEqual(len(rs), 0)

    def test_findNumber(self):
        for name in ['Bob', 'Tom', 'Alice', 'Newton', 'Frank', 'Grace']:
            s = TestSimple(name=name, gender=True, birth=date(2011, 1, 1), current=datetime.now())
            s.save()
        count = TestSimple.findNumber('count(*)')
        self.assertEqual(count, 6)
        count = TestSimple.findNumber('count(*)', 'name like ?', ('%o%',))
        self.assertEqual(count, 3)
        avg = TestSimple.findNumber('avg(age)')
        self.assertEqual(avg, 20.0, 0.1)

    def test_nextid(self):
        s = set()
        N = 100000
        for i in range(N):
            x = model.nextid()
            s.add(x)
        self.assertEqual(N, len(s))

if __name__ == '__main__':
    unittest.main()
