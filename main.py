#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import sys
import time
import json
from Common import mail , filehandle

reload(sys)
sys.setdefaultencoding('utf8')

class WooYun(filehandle.FileHandle,mail.MailCreate):
    """docstring for WooYun"""
    def __init__(self,keysfile,errorIdfile):
        super(WooYun, self).__init__('WooYun监看机器人',keysfile,errorIdfile)
        self.wooyunSubmit = 'http://api.wooyun.org/bugs/submit'
        self.errorID = self.errorIdread()
        self.keyWordlist = self.keyWordsread()
        self.fileMd5 = self.fileMd5get()
        self.count = 0

        self.


if __name__ == '__main__':
    test = WooYun('KeyWords.txt' , 'ErrorId360.txt')

