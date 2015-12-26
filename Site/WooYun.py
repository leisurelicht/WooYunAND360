#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import time
import socket
import logging
from bs4 import BeautifulSoup
from Common import mail, filehandle, database
from Common.common import *

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()


class WooYun(filehandle.FileHandle, mail.MailCreate):
    """docstring for WooYun"""
    def __init__(self, keys_file, events_id_file):
        super(WooYun, self).__init__('WooYun监看机器人', keys_file, events_id_file)
        self.wooyun_url = 'http://api.wooyun.org/bugs/submit'
        self.events_id_list = self.events_id_read()
        self.key_words_list = self.key_words_read
        self.fileMd5 = self.file_md5_get
        self.count = 0
        socket.setdefaulttimeout = 30
        self.headers = {
            'Host': 'www.wooyun.org',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate', 'DNT': '1',
            'Referer': 'http://www.wooyun.org/index.php',
            'Cookie': 'Hm_lvt_c12f88b5c1cd041a732dea597a5ec94c=1443363836,1443364000,1443364038,1444381968; bdshare_firstime=1423619234389; \
            __cfduid=d037debb012835d005205cd496bcdaf321437360051; PHPSESSID=un87r2ohvbnilkehpp5ckkgcd5; \
            Hm_lpvt_c12f88b5c1cd041a732dea597a5ec94c=1444382107',
            'Connection': 'keep-alive'
        }
        self.con = database.connect_wooyun()

    def __del__(self):
        print 'WooYun监看机器人 is shutdown'

    def data_request(self, url=None):
        """
        从乌云API获取json格式的数据
        返回json格式的数据
        :param url:
        """
        print 'WooYun_dataRequest'
        url = url or self.wooyun_url
        while True:
            try:
                if self.count > 10:
                    self.send_text_email('Important Program Exception', 'Target url can not reach', 'ExceptionInfo')
                    self.count = 0
                    time.sleep(100)
                    continue
                text = requests.get(url, timeout=30)
            except socket.timeout:
                time.sleep(30)
                self.count += 1
                continue
            except requests.exceptions.ReadTimeout:
                time.sleep(10)
                self.count += 1
                continue
            except requests.exceptions.ConnectTimeout:
                time.sleep(60)
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
            except requests.exceptions.HTTPError as e:
                error_text = exception_format(get_current_function_name(), e)
                self.send_text_email('Important Program Exception', error_text, 'ExceptionInfo')
                time.sleep(600)
                self.count += 1
                continue
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
                self.count += 1
                continue
            else:
                if text.status_code == 200:
                    self.count = 0
                    return text
                elif text.status_code == 522:
                    continue
                elif text.status_code == 504:
                    time.sleep(30)
                    self.count += 1
                    continue
                else:
                    error_text = "Page Code %s " % text.status_code
                    self.send_text_email('Page Error', error_text, 'ExceptionInfo')
                    continue

    def data_achieve(self, text):
        """
        将json格式的数据取出
        :param text: 来自data_request函数
        """
        print 'WooYun_dataAchieve'
        while 1:
            try:
                data = text.json()
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
                text = self.data_request()
            else:
                md5value = self.file_md5_get
                if md5value != self.fileMd5:
                    self.key_words_list = self.key_words_read
                    self.fileMd5 = md5value
                return data

    def description_achieve(self, url):
        """
        获取WooYun事件页面中的描述部分
        返回描述部分
        :param url:
        """
        print 'WooYun_descriptionAchieve'
        while True:
            try:
                page = requests.get(url, headers=self.headers, timeout=30)
            except requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout:
                time.sleep(30)
                continue
            except requests.exceptions.HTTPError as e:
                error_text = exception_format(get_current_function_name(), e)
                self.send_text_email('Important Program Exception', error_text, 'ExceptionInfo')
                time.sleep(60)
                continue
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                self.send_text_email('Program Exception 1', error_text, 'ExceptionInfo')
                continue
            else:
                if page.status_code == 200:
                    try:
                        soup = BeautifulSoup(page.content)
                    except Exception as e:
                        error_text = exception_format(get_current_function_name(), e)
                        self.send_text_email('Program Exception 2', error_text, 'ExceptionInfo')
                        continue
                    else:
                        des = soup.find(class_="detail wybug_description").string.strip()
                        return des
                else:
                    print page.status_code
                    continue

    def key_words_check(self, data):
        """
        检查获得的标题中是否含有要监看的关键字
        内部调用sendRecord()
        没有返回值
        :param data: 事件标题组成的list
        """
        print 'WooYun_key_words_check'

        try:
            for detail in data:
                for key1, values in self.key_words_list.iteritems():
                    if detail.get('title').find(key1) != -1:
                        if values:
                            for value in values:
                                # 1. 检查第二关键字是否存在
                                if value.get('KEY2') is not None:
                                    if detail.get('title').find(value.get('KEY2')) != -1:
                                        # print '1.',detail.get('title')
                                        self.send_record(detail.get('title').strip(), detail.get('link'),
                                                         detail.get('id'))
                                        # else: #二级关键词不中的话继续查域名和内容
                                        # 2. 进入页面检查厂商域名
                                        # 3. 在页面内查找是否存在第二关键字
                                elif value.get('KEY2') is None:
                                    # print '2.',detail.get('title')
                                    self.send_record(detail.get('title').strip(), detail.get('link'), detail.get('id'))
                        else:
                            # print '3.',detail.get('title')
                            self.send_record(detail.get('title').strip(), detail.get('link'), detail.get('id'))
                    else:
                        print "事件中不存在监看关键词,开始检测下一个关键词"

        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            print error_text
            # self.send_text_email( 'Program Exception' , errortext , 'ExceptionInfo' )

    def send_record(self, event_title, event_url, event_id):
        """
        调用邮件发送函数并记录被发送的事件ID
        没有返回值
        函数内调用sendTextEmail()
        :param event_id:
        :param event_url:
        :param event_title:
        """
        print 'WooYun_sendRecord'
        check_result = self.events_id_check(event_id, self.events_id_list)
        if 0 not in check_result:
            try:
                self.send_text_email(event_title, event_url, 'securityInfo')
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                print error_text
                # self.send_text_email( 'Program Exception' , error_text , 'ExceptionInfo' )
            else:
                self.events_id_list.append(event_id)
                self.events_id_add(event_id)
        else:
            print event_title, " Same thing was sent,did not send same mail to everyone"


if __name__ == '__main__':
    robot_WooYun = WooYun('../Config/KeyWords.txt', '../Events/EventsID.txt')
    robot_WooYun.data_achieve(robot_WooYun.data_request())
