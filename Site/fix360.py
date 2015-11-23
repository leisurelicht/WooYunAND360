#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import re
import sys
import time
import random
import logging
from bs4 import BeautifulSoup
from Common import mail , filehandle

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()

class fix360(filehandle.FileHandle,mail.MailCreate):
    """docstring for fix360"""
    def __init__(self, keysfile,eventsIdfile):
        super(fix360, self).__init__('360补天监看机器人',keysfile,eventsIdfile)
        self._360Fixurl = 'http://loudong.360.cn/vul/list'
        self._360baseurl = 'http://loudong.360.cn'
        self.eventsIdlist = self.eventsIdread()
        self.keyWordlist = self.keyWordsread()
        self.fileMd5 = self.fileMd5get()
        self.html = 0
        self.count = 0

    def __del__(self):
        print '360监看机器人 is shutdown'

    def dataRequest(self):
        '''
        从360补天获取最新的10页事件
        返回一个存储网页的list
        '''
        print '360_dataRequest'
        urls = []
        htmls = []
        for num in range(1,11):
            urls.append(self._360Fixurl + '/page/%s' % num )
        for url in urls:
            while True:
                try:
                    page = requests.get( url , timeout = 30)
                except requests.exceptions.ConnectionError:
                    time.sleep(30)
                    continue
                except requests.exceptions.ConnectTimeout:
                    time.sleep(60)
                    continue
                except requests.exceptions.HTTPError as e:
                    errortext = "Error in function : \" %s \" ,\n \
                    Error name is : \" %s \" ,\n \
                    Error type is : \" %s \" ,\n \
                    Error Message is : \" %s \" ,\n \
                    Error doc is : \" %s \" \n" % \
                    (sys._getframe().f_code.co_name,\
                     e.__class__.__name__,\
                     e.__class__,\
                     e,\
                     e.__class__.__doc__)
                    self.sendTextEmail( 'Important Program Exception' , errortext , 'ExceptionInfo' )
                    time.sleep(600)
                    continue
                except Exception as e:
                    errortext = "Error in function : \" %s \" ,\n \
                    Error name is : \" %s \" ,\n \
                    Error type is : \" %s \" ,\n \
                    Error Message is : \" %s \" ,\n \
                    Error doc is : \" %s \" \n" % \
                    (sys._getframe().f_code.co_name,\
                     e.__class__.__name__,\
                     e.__class__,\
                     e,\
                     e.__class__.__doc__)
                    self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
                    continue
                else:
                    if page.status_code == 200:
                        htmls.append(page.content) #get page content
                        #time.sleep(random.randint(0,60))
                        break
                    else:
                        errortext = "Page Code %s " % page.status_code
                        self.sendTextEmail( 'Page Error' , errortext , 'ExceptionInfo' )
                        continue
        return htmls

    def dataAchieve(self,pages):
        '''
        获取事件名和链接
        返回一个{链接:事件名}型的字典
        '''
        print '360_dataAchieve'
        events = {}
        for page in pages:
            while True:
                try:
                    soup = BeautifulSoup(page,"html5lib")
                except Exception as e:
                    errortext = "Error in function : \" %s \" ,\n \
                    Error name is : \" %s \" ,\n \
                    Error type is : \" %s \" ,\n \
                    Error Message is : \" %s \" ,\n \
                    Error doc is : \" %s \" \n" % \
                    (sys._getframe().f_code.co_name,\
                     e.__class__.__name__,\
                     e.__class__,\
                     e,\
                     e.__class__.__doc__)
                    self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
                    self.dataRequest()
                else:
                    titles = soup.find_all(href=re.compile("/vul/info/qid"))
                    #title2 = soup.find_all(href=re.compile("/company/info/id/"))
                    #title3 = soup.find_all(href=re.compile("/vul/search/"))
                    #titles = title1 + title2 +title3
                    for title in titles:
                        events[ title['href'] ] = title.string.strip()
                    break
        return events

    def keyWordscheck(self,events):
        '''
        检查获得的标题中是否含有要监看的关键字
        函数内调用sendRecord()
        没有返回值
        '''
        print '360_keyWordscheck'
        tempFileMd5 = self.fileMd5check(self.fileMd5)
        if tempFileMd5:
            self.fileMd5 = tempFileMd5
            self.keyWordlist = self.keyWordsread()
        try:
            for (_360url,_360title) in events.items():
                for Key in self.keyWordlist:
                    if Key in _360title:
                        self.sendRecord( _360title , self._360baseurl + _360url , _360url.split('/')[-1] )
        except Exception as e:
            errortext = "Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,\
             e.__class__.__name__,\
             e.__class__,\
             e,\
             e.__class__.__doc__)
            self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )

    def sendRecord(self,eventTitle,eventURL,eventID):
        '''
        调用邮件发送函数并记录被发送的事件ID
        没有返回值
        函数内调用sendTextEmail()
        '''
        print '360_sendRecord'
        checkresult = self.eventsIdCheck(eventID,self.eventsIdlist)
        if 0 not in checkresult:
            try:
                #pass #test to use
                self.sendTextEmail(eventTitle,eventURL,'securityInfo')
            except Exception as e:
                errortext = "Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,\
                e.__class__.__name__,\
                e.__class__,\
                e,\
                e.__class__.__doc__)
                print errortext
                #self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
            else:
                self.eventsIdlist.append( eventID )
                self.eventsIdadd( eventID )
        else:
            print eventTitle," Same thing was sent,did not send same mail to everyone"


if __name__ == '__main__':
    robot = fix360('keyWords.txt' , './Events/EventsID360.txt')
    robot.keyWordscheck(robot.dataAchieve(robot.dataRequest()))




