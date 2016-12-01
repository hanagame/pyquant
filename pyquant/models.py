' models definition '

__author__ = 'Michael Liao'

from pyquant import model

class Vendor(model.Model):
    code = model.StringField()
    name = model.StringField()
    url = model.StringField()

class Exchange(model.Model):
    code = model.StringField()
    name = model.StringField()
    currency = model.StringField()
    timezone = model.StringField()

class Symbol(model.Model):
    exchange_id = model.IntegerField()
    code = model.StringField()
    name = model.StringField()
    currency = model.StringField()
    industry = model.StringField(default='')
    area = model.StringField(default='')
    outstanding = model.FloatField(default=0.0)
    total = model.FloatField(default=0.0)
    is_index = model.BooleanField(default=False)

class Account(model.Model):
    name = model.StringField()
    exchange_id = model.IntegerField()
    currency = model.StringField()
    kind = model.StringField()
    symbol = model.StringField()
    balance = model.FloatField()

class K1DPrice(model.Model):
    ' K price for 1 day '
    vendor_id = model.IntegerField()
    symbol_id = model.IntegerField()
    price_date = model.DateField()
    open_price = model.FloatField()
    high_price = model.FloatField()
    low_price = model.FloatField()
    close_price = model.FloatField()
    adj_close_price = model.FloatField()
    volume = model.FloatField()

class K1MPrice(model.Model):
    ' K price for 1 min '
    vendor_id = model.IntegerField()
    symbol_id = model.IntegerField()
    price_date = model.DateField()
    open_price = model.FloatField()
    high_price = model.FloatField()
    low_price = model.FloatField()
    close_price = model.FloatField()
    adj_close_price = model.FloatField()
    volume = model.FloatField()

class K5MPrice(model.Model):
    ' K price for 5 min '
    vendor_id = model.IntegerField()
    symbol_id = model.IntegerField()
    price_date = model.DateField()
    open_price = model.FloatField()
    high_price = model.FloatField()
    low_price = model.FloatField()
    close_price = model.FloatField()
    adj_close_price = model.FloatField()
    volume = model.FloatField()

class K10MPrice(model.Model):
    ' K price for 10 min '
    vendor_id = model.IntegerField()
    symbol_id = model.IntegerField()
    price_date = model.DateField()
    open_price = model.FloatField()
    high_price = model.FloatField()
    low_price = model.FloatField()
    close_price = model.FloatField()
    adj_close_price = model.FloatField()
    volume = model.FloatField()

class K1HPrice(model.Model):
    ' K price for 1 hour '
    vendor_id = model.IntegerField()
    symbol_id = model.IntegerField()
    price_date = model.DateField()
    open_price = model.FloatField()
    high_price = model.FloatField()
    low_price = model.FloatField()
    close_price = model.FloatField()
    adj_close_price = model.FloatField()
    volume = model.FloatField()
