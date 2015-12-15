#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import sys
import time
import json
import socket
import logging
from bs4 import BeautifulSoup
from Common import mail, filehandle

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()

class WooYun(filehandle.FileHandle,mail.MailCreate):
    """docstring for WooYun"""
    def __init__(self,keysfile,eventsIdfile):
        super(WooYun, self).__init__('WooYun监看机器人',keysfile,eventsIdfile)
        self.wooyun_url = 'http://api.wooyun.org/bugs/submit'
        self.eventsIdlist = self.eventsIdread()
        self.keyWordslist = self.keyWordsread()
        self.fileMd5 = self.fileMd5get()
        self.count = 0
        socket.setdefaulttimeout = 30
        self.headers = {
        'Host' : 'www.wooyun.org',
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding' : 'gzip, deflate','DNT' : '1',
        'Referer' : 'http://www.wooyun.org/index.php',
        'Cookie' : 'Hm_lvt_c12f88b5c1cd041a732dea597a5ec94c=1443363836,1443364000,1443364038,1444381968; bdshare_firstime=1423619234389; __cfduid=d037debb012835d005205cd496bcdaf321437360051; PHPSESSID=un87r2ohvbnilkehpp5ckkgcd5; Hm_lpvt_c12f88b5c1cd041a732dea597a5ec94c=1444382107',
        'Connection' : 'keep-alive'
        }

    def __del__(self):
        print 'WooYun监看机器人 is shutdown'

    def dataRequest(self,url=None):
        '''
        从乌云API获取json格式的数据
        返回json格式的数据
        '''
        print 'WooYun_dataRequest'
        url = url or self.wooyun_url
        while True:
            try:
                if self.count > 10:
                    self.sendTextEmail( 'Important Program Exception' , 'Target url can not reach' , 'ExceptionInfo' )
                    self.count = 0
                    time.sleep(100)
                    continue
                text = requests.get( url , timeout = 30 )
            except socket.timeout:
                time.sleep(30)
                self.count += 1
                continue
            except requests.exceptions.Timeout:
                time.sleep(30)
                self.count += 1
                continue
            except requests.exceptions.ConnectionError:
                time.sleep(30)
                self.count += 1
                continue
            except requests.exceptions.ConnectTimeout:
                time.sleep(60)
                self.count += 1
                continue
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
                self.count += 1
                continue
            except requests.exceptions.HTTPError as e:
                errortext = "Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,\
                 e.__class__.__name__,
                 e.__class__,
                 e,
                 e.__class__.__doc__)
                self.sendTextEmail( 'Important Program Exception' , errortext , 'ExceptionInfo' )
                time.sleep(600)
                self.count += 1
                continue
            except Exception as e:
                errortext = "Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,
                 e.__class__.__name__,
                 e.__class__,
                 e,
                 e.__class__.__doc__)
                self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
                self.count += 1
                continue
            else:
                if text.status_code == 200:
                    self.count = 0
                    break
                elif text.status_code == 522:
                    continue
                elif text.status_code == 504:
                    time.sleep(30)
                    self.count += 1
                    continue
                else:
                    errortext = "Page Code %s " % text.status_code
                    self.sendTextEmail( 'Page Error' , errortext , 'ExceptionInfo' )
                    continue
        return text


    def dataAchieve(self,text):
        '''
        将json格式的数据取出
        '''
        print 'WooYun_dataAchieve'
        try :
            data = text.json()
            #raise Exception("data is not json")
        except Exception as e:
            errortext = "Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,
            e.__class__.__name__,
            e.__class__,
            e,
            e.__class__.__doc__)
            self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
            self.dataRequest()
        else:
            md5value = self.fileMd5get()
            if md5value != self.fileMd5:
                self.keyWordsread()
                self.fileMd5 = md5value
        return data

    def descriptionAchieve(self,url):
        '''
        获取WooYun事件页面中的描述部分
        返回描述部分
        '''
        print 'WooYun_descriptionAchieve'
        while True:
            try:
                page = requests.get( url , headers = self.headers , timeout = 30 )
            except requests.exceptions.ConnectionError , requests.exceptions.ConnectTimeout:
                time.sleep(30)
                continue
            except requests.exceptions.HTTPError as e:
                errortext = "Error is Function : \" %s \" , \n \
                Error Name is : \" %s \" , \n \
                Error Type is : \" %s \" , \n \
                Error Message is : \" %s \" , \n \
                Error Doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,
                 e.__class__.__name__,
                 e.__class__,
                 e,
                 e.__class__.__doc__)
                self.sendTextEmail( 'Important Program Exception' , errortext , 'ExceptionInfo')
                time.sleep(60)
                continue
            except Exception as e:
                errortext = "Error is Function : \" %s \" , \n \
                Error Name is : \" %s \" , \n \
                Error Type is : \" %s \" , \n \
                Error Message is : \" %s \" , \n \
                Error Doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,\
                 e.__class__.__name__,\
                 e.__class__,\
                 e,\
                 e.__class__.__doc__)
                self.sendTextEmail( 'Program Exception 1' , errortext , 'ExceptionInfo' )
                continue
            else:
                if page.status_code == 200:
                    try:
                        soup = BeautifulSoup(page.content)
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
                        self.sendTextEmail( 'Program Exception 2' , errortext , 'ExceptionInfo' )
                        continue
                    else:
                        des = soup.find(class_="detail wybug_description").string.strip()
                        break

                else:
                    print page.status_code
                    break
        return des


    def keyWordscheck(self,data):
        '''
        检查获得的标题中是否含有要监看的关键字
        内部调用sendRecord()
        没有返回值
        '''
        print 'WooYun_keyWordscheck'

        try:
            for detail in data:
                #print detail.get('title')
                for key1, values in self.keyWordslist.iteritems():
                    if detail.get('title').find(key1) != -1:
                        for value in values:
                            # 1. 检查第二关键字是否存在
                            if detail.get('title').find(value['KEY2']) != -1:
                                #print detail.get('title')
                                self.sendRecord(detail.get('title').strip(),detail.get('link'),detail.get('id'))
                                break
                            #else：
                            # 2. 进入页面检查厂商域名
                            # 3. 在页面内查找是否存在第二关键字

        except Exception as e:
            errortext = "Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,
             e.__class__.__name__,
             e.__class__,
             e,
             e.__class__.__doc__)
            print errortext
            #self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )

    def sendRecord(self,eventTitle,eventURL,eventID):
        '''
        调用邮件发送函数并记录被发送的事件ID
        没有返回值
        函数内调用sendTextEmail()
        '''
        print 'WooYun_sendRecord'
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
                (sys._getframe().f_code.co_name,
                e.__class__.__name__,
                e.__class__,
                e,
                e.__class__.__doc__)
                print errortext
                #self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
            else:
                self.eventsIdlist.append( eventID )
                self.eventsIdadd( eventID )
        else:
            print eventTitle," Same thing was sent,did not send same mail to everyone"

if __name__ == '__main__':
    test = WooYun('KeyWords.txt' , './Events/EventsID.txt')
    #data = test.dataAchieve(robot)
    #test.keyWordscheck(data)
    #print robot
    #print test.descriptionAchieve('http://www.wooyun.org/bugs/wooyun-2015-0145547')

