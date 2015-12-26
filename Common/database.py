#! usr/bin/env python
# -*- coding=utf-8 -*-
import pymongo
from common import *


def connect_wooyun(name):
    try:
        client = pymongo.MongoClient("localhost",'27017')
    except Exception as e:
        error_text = exception_format(get_current_function_name(), e)
        print error_text
    else:
        db = client.WooYunand360
        collection = db.wooyun
        return collection

def insert_data(collection, data):
    if isinstance(data, list):
        collection.insert_manny(data)
    else:
        collection.insert(data)




if __name__=="__main__":
    con=connect_wooyun("wooyun")
    #insert_data(con, {"name":"freebuf"})
