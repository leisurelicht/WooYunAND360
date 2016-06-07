#! usr/bin/env python
# -*- coding=utf-8 -*-

import sys
# import inspect
import traceback


# def get_current_function_name():
#     """
#     动态的获取当前函数名
#     :return: 函数名
#     """
#     return inspect.stack()[1][3]

def exception_format(e):
    """
    :param e: 异常
    :return: 格式化后的信息
    """
    print "execption_format"
    tb_type, tb_val, exc_tb = sys.exc_info()
    for filename , linenum, funcname, source in traceback.extract_tb(exc_tb):
        error_text = " \
        Error in file       : \" {0:s} \" ,\n \
        Error in function   : \" {1:s} \" ,\n \
        Error line          : \" {2:d} \" ,\n \
        Error source        : \" {3:s} \" ,\n \
        Error name is       : \" {4:s} \" ,\n \
        Error type is       : \" {5:s} \" ,\n \
        Error Message is    : \" {6:s} \" ,\n \
        Error doc is        : \" {7:s} \" , \n " \
        .format(filename,
                funcname,
                linenum,
                source,
                e.__class__.__name__,
                e.__class__,
                e,
                e.__class__.__doc__)

        return error_text
