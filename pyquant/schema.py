' models definition '

__author__ = 'Michael Liao'

import sys

from pyquant import model
from pyquant import models

if __name__ == '__main__':
    drop = len(list(filter(lambda arg: arg=='--drop', sys.argv))) > 0
    names = dir(models)
    for name in names:
        cls = getattr(models, name)
        if type(cls) == model.ModelMetaclass:
            print('\n-- init %s:' % cls.__table__)
            if drop:
                print('drop table if exists %s;' % cls.__table__)
            print(cls.__ddl__)
