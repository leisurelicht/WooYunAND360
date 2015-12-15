#! usr/bin/env python
# -*- coding=utf-8 -*-

import os
import sys
import json
import logging
import hashlib
import mail

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()


class FileHandle(mail.MailCreate):
    """docstring for FileHandle"""
    def __init__(self, sendername,keysfile , eventsIdfile):
        super(FileHandle, self).__init__(sendername)
        self.keyfile = keysfile
        self.eventsIdfile = eventsIdfile

    def eventsIdread(self):
        '''
        从文件中读取已经发送过邮件的事件ID
        返回一个list
        '''
        print "eventsIdread"
        errorId = []
        if os.path.exists( self.eventsIdfile ):
            with open( self.eventsIdfile ) as errors:
                for error in errors:
                    if not error.isspace():
                        errorId.append( error.strip() )
            return errorId
        else:
            filepath , filename = os.path.split( self.eventsIdfile )
            if not os.path.exists( filepath ):
                os.makedirs( filepath )
            else:
                tmp = open( self.eventsIdfile,'a' )
                tmp.close()


    def eventsIdadd(self,newId):
        '''
        向EventsID.txt文件中加入一个事件ID
        返回一个list
        '''
        tmp = open( self.eventsIdfile,'a' )
        tmp.write(newId+'\n')
        tmp.close()

    def keyWordsread(self):
        '''
        从文件中读取需要监看的关键字
        返回一个json格式的数据
        '''
        print 'keyWordsread'
        if os.path.exists(self.keyfile):
            with open(self.keyfile) as keys:
                tmp = keys.read()
            try:
                keywordslist = json.loads(tmp)
            except Exception as e:
                errortext = "Error in functon : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" , \n " % \
                (sys._getframe().f_code.co_name,
                 e.__class__.__name__,
                 e.__class__,
                 e,
                 e.__class__.__doc__)
                self.sendTextEmail("keyWordsread",errortext,"ExceptionInfo")

            return keywordslist
        else:
            tmp = open(self.keyfile, 'a')
            tmp.close()


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
            errortext = "Error in functon : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" , \n " % \
            (sys._getframe().f_code.co_name,
             e.__class__.__name__,
             e.__class__,
             e,
             e.__class__.__doc__)
            #print errortext
            self.sendTextEmail("fileMd5check",errortext,"ExceptionInfo")
        return md5temp

    def fileMd5check(self,oldfilemd5):
        '''
        检查文件的MD5值,确定文件是否发生改变
        没有发生改变返回False
        发生改变返回新的MD5值
        '''
        print 'fileMd5check'
        try:
            #filemd5 = hashlib.md5()
            #with open(self.keyfile) as filetemp:
            #    filemd5.update( filetemp.read().strip() )
            #    md5temp = filemd5.hexdigest()
            md5temp = self.fileMd5get()
        except Exception as e:
            errortext = "Error in functon : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" , \n " % \
            (sys._getframe().f_code.co_name,
             e.__class__.__name__,
             e.__class__,
             e,
             e.__class__.__doc__)
            #print errortext
            self.sendTextEmail("fileMd5check",errortext,"ExceptionInfo")
        else:
            if oldfilemd5 == md5temp:
                return False
            else:
                return md5temp

    def eventsIdCheck(self,newId,eventsIdlist):
        '''
        通过ID确定事件是否已经被发送过
        返回一个list
        如果list里包含0,则已被发送过
        '''
        print 'eventsIdCheck'
        temp = []
        if ( len(eventsIdlist) > 0 ):
            for eventId in eventsIdlist:
                 if not eventId.isspace():
                    temp.append( cmp( eventId,newId ) )
        return temp



if __name__ == '__main__':
    test = FileHandle('filehandle','KeyWords.txt' , '../Events/EventsID360.txt')
    #print test.eventsIdread()
    #for key in test.keyWordsread():
    #    print key
    #a=test.fileMd5get()
    #print a

    #while True:
    #    b=test.fileMd5check(a)
    #    print b
    #    if b:
    #        a = b
    #    time.sleep(5)
    print test.eventsIdread()


