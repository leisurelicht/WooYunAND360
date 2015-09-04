#! usr/bin/env python
#-*- coding=utf-8 -*-

import os
import sys
import time
import hashlib
import mail

reload(sys)
sys.setdefaultencoding('utf8')

class FileHandle(mail.MailCreate):
    """docstring for FileHandle"""
    def __init__(self, sendername,keysfile , errorIdfile):
        super(FileHandle, self).__init__(sendername)
        self.keyfile = keysfile
        self.errorIdfile = errorIdfile

    def errorIdread(self):
        '''
        从文件中读取已经发送过邮件的事件ID
        返回一个list
        '''
        print "errorIdread"
        errorId = []
        if os.path.exists( self.errorIdfile ):
            with open( self.errorIdfile ) as errors:
                for error in errors:
                    if not error.isspace():
                        errorId.append( error.strip() )

        return errorId

    def keyWordsread(self):
        '''
        从文件中读取需要监看的关键字
        返回一个list
        '''
        print 'keyWordsread'
        keyWordslist = []
        if os.path.exists( self.keyfile ):
            with open( self.keyfile ) as keys:
                for key in keys:
                    if not key.isspace():
                        keyWordslist.append( key.strip() )
        return keyWordslist

    def fileMd5get(self):
        '''
        获取文件的MD5值
        返回一个MD5值
        '''
        print 'fileMd5get'
        try:
            filemd5 = hashlib.md5()
            with open(self.keyfile) as filetemp:
                filemd5.update( filetemp.read().strip() )
                md5temp = filemd5.hexdigest()
        except Exception as e:
            print e
        return md5temp

    def fileMd5check(self,oldfilemd5):
        '''
        检查文件的MD5值,确定文件是否发生改变
        没有发生改变返回False
        发生改变返回新的MD5值
        '''
        print 'fileMd5check'
        try:
            filemd5 = hashlib.md5()
            with open(self.keyfile) as filetemp:
                filemd5.update( filetemp.read().strip() )
                md5temp = filemd5.hexdigest()
        except Exception as e:
            errortext = "Error in functon : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" , \n " % \
            (sys._getframe().f_code.co_name,\
            e.__class__.__name__,\
            e.__class__,\
            e,\
            e.__class__.__doc__)
            #print errortext
            self.sendTextEmail("fileMd5check",errortext,"ExceptionInfo")
        else:
            if oldfilemd5 == md5temp:
                return False
            else:
                return md5temp



if __name__ == '__main__':
    test = FileHandle('filehandle','KeyWords.txt' , 'ErrorId360.txt')
    #print test.errorIdread()
    #for key in test.keyWordsread():
    #    print key
    a=test.fileMd5get()
    print a

    while True:
        b=test.fileMd5check(a)
        print b
        if b:
            a = b
        time.sleep(5)

