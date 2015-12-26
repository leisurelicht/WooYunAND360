#! usr/bin/env python
# -*- coding=utf-8 -*-
import sys


def exception_format(e):
    """
    :param e:
    :return:
    """
    error_text = "Error in functon : \" {0:s} \" ,\n \
                Error name is : \" {1:s} \" ,\n \
                Error type is : \" {2:s} \" ,\n \
                Error Message is : \" {3:s} \" ,\n \
                Error doc is : \" {4:s} \" , \n " \
                    .format(sys._getframe().f_code.co_name,
                            e.__class__.__name__,
                            e.__class__,
                            e,
                            e.__class__.__doc__)
    return error_text
