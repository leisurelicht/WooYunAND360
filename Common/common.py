#! usr/bin/env python
# -*- coding=utf-8 -*-

import inspect

# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

def get_current_function_name():
    """
    动态的获取当前函数名
    :return: 函数名
    """
    return inspect.stack()[1][3]

def exception_format(function_name, e):
    """
    :param function_name: 抛出异常的函数名
    :param e: 异常
    :return: 格式化后的信息
    """
    error_text = "     Error in functon : \" {0:s} \" ,\n \
    Error name is : \" {1:s} \" ,\n \
    Error type is : \" {2:s} \" ,\n \
    Error Message is : \" {3:s} \" ,\n \
    Error doc is : \" {4:s} \" , \n " \
    .format(function_name,
            e.__class__.__name__,
            e.__class__,
            e,
            e.__class__.__doc__)
    return error_text
