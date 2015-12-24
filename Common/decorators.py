#! usr/bin/env python
# -*- coding=utf-8 -*_
import functools
from datetime import datetime


def robot_start_sign(arg):
    def sign(func):
        @functools.wraps(func)
        def deco():
            print '*'*100
            print('*'*18+arg+' 开始运行...! The time is: %s' % datetime.now()+'*'*10)
            print '*'*100
            time1 = datetime.now()
            func()
            print '*'*100
            print('*'*18+arg+' 运行结束! The time is: %s' % datetime.now()+'*'*10)
            print '*'*100
            print '*'*25, "本次运行共耗时,共耗时: ", (datetime.now()-time1), '*'*25
        return deco
    return sign
