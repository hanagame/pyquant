#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

from decimal import Decimal

import time
import itertools
import logging

from pyquant import database
from pyquant.xdict import Dict

# generate next id:

idcounter = itertools.count()

def nextid():
    '''
    generate next bigint.
    '''
    return (int(time.time()) << 20) + (next(idcounter) % 0x100000)

def _create_args_string(num):
    return ', '.join('?' * num)

_field_seq = 0

class Field(object):

    def __init__(self, name, column_type, default):
        global _field_seq
        _field_seq = _field_seq + 1
        self.name = name
        self.column_type = column_type
        self.default = default
        self.seq = _field_seq

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):

    def __init__(self, name=None, default='', ddl='varchar(50)'):
        super().__init__(name, ddl, default)

class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', default)

class IntegerField(Field):

    def __init__(self, name=None, default=0):
        super().__init__(name, 'bigint', default)

class FloatField(Field):

    def __init__(self, name=None, default=0.0):
        super().__init__(name, 'real', default)

class DateField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'date', default)

class DateTimeField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'datetime', default)

class TextField(Field):

    def __init__(self, name=None, default=''):
        super().__init__(name, 'text', default)

class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name=='Model':
            return type.__new__(cls, name, bases, attrs)
        table_name = attrs.get('__table__', name)
        logging.info('Found model: %s (table: %s)' % (name, table_name))
        mappings = dict()
        fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                fields.append(k)
        for k in mappings.keys():
            attrs.pop(k)
        # add created_at, updated_at, version:
        mappings['created_at'] = FloatField('created_at', time.time)
        mappings['updated_at'] = FloatField('updated_at', time.time)
        mappings['version'] = IntegerField('version', 0)
        fields.append('created_at')
        fields.append('updated_at')
        fields.append('version')
        # add id to last field:
        f_id = IntegerField('id', nextid)
        f_id.seq = 0 # set seq of id to 0
        mappings['id'] = f_id
        fields.append('id')
        name_and_field = [(k, v) for k, v in mappings.items()]
        sorted_name_and_field = sorted(name_and_field, key=lambda t: t[1].seq)
        for name, field in sorted_name_and_field:
            logging.info('    mapping: %s ==> %s' % (name, mappings[name]))

        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = table_name
        attrs['__fields__'] = fields # 所有属性名称
        attrs['__select__'] = 'select * from %s' % table_name
        attrs['__insert__'] = 'insert into %s (%s) values (%s)' % (table_name, ', '.join(fields), ', '.join('?' * len(fields)))
        attrs['__update__'] = 'update %s set %s where id=?' % (table_name, ', '.join(map(lambda f: '%s=?' % f, filter(lambda f: f!='id', fields))))
        attrs['__delete__'] = 'delete from %s where id=?' % table_name
        attrs['__ddl__'] = 'create table %s (%s, primary key (id)) engine=innodb;' % (table_name, ', '.join(['%s %s not null' % (name, f.column_type) for name, f in sorted_name_and_field]))
        return type.__new__(cls, name, bases, attrs)

class Model(Dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __str__(self):
        return '''<Model: %s>
    SELECT: %s
    INSERT: %s
    UPDATE: %s
    DELETE: %s
    DDL: %s
</Model: %s>
''' % (self.__table__, self.__select__, self.__insert__, self.__update__, self.__delete__, self.__ddl__, self.__table__)

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value

    @classmethod
    def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        else:
            args = list(args)
        orderby = kw.get('orderby', None)
        if orderby:
            sql.append('order by')
            sql.append(orderby)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = database.select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = database.select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        num = rs[0]['_num_']
        if isinstance(num, Decimal):
            num = float(num)
        return num

    @classmethod
    def find(cls, pk):
        ' find object by primary key. '
        rs = database.select('%s where id=?' % cls.__select__, (pk, ), 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        rows = database.execute(self.__insert__, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)

    def update(self):
        args = list(map(self.getValue, self.__fields__))
        rows = database.execute(self.__update__, args)
        if rows != 1:
            logging.warning('failed to update by primary key: affected rows: %s' % rows)

    def remove(self):
        args = [self.getValue('id')]
        rows = database.execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to remove by primary key: affected rows: %s' % rows)
