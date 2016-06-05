#! usr/bin/env python
# -*- coding=utf-8 -*-

import pymongo
from common import exception_format, get_current_function_name

host = "localhost"
port = 27017

def connect_wooyun():
    try:
        client = pymongo.MongoClient(host, port)
    except Exception as e:
        error_text = exception_format(get_current_function_name(), e)
        print error_text
    else:
        db = client.WooYunand360
        collection = db.wooyun
        return collection


def connect_fixsky():
    try:
        client = pymongo.MongoClient(host, port)
    except Exception as e:
        error_text = exception_format(get_current_function_name(), e)
        print error_text
    else:
        db = client.WooYunand360
        collection = db.fixsky
        return collection


def connect_freebuf():
    try:
        client = pymongo.MongoClient(host, port)
    except Exception as e:
        error_text = exception_format(get_current_function_name(), e)
        print error_text
    else:
        db = client.WooYunand360
        collection = db.freebuf
        return collection


def insert_data(collection, database):
    try:
        if isinstance(database, list):
            collection.insert_many(database)
        elif isinstance(database, dict):
            collection.insert_one(database)
    except Exception as e:
        error_text = exception_format(get_current_function_name(), e)
        print error_text


def remove_date(collection):
    collection.remove()


if __name__ == "__main__":
    con = connect_wooyun()
    #con.remove()
    #for data in con.find():
    #    print data['title']

        # insert_data(con, {"name":"freebuf"})
