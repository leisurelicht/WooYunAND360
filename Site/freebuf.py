#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import re
import time
import logging
from bs4 import BeautifulSoup
from Common import mail, filehandle
from Common.common import *

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()


class FreeBuf(filehandle.FileHandle, mail.MailCreate):
    """docstring for FreeBuf"""
    def __init__(self, keys_file, events_id_file):
        super(FreeBuf, self).__init__('漏洞盒子监看机器人', keys_file, events_id_file)
        self.freebuf_url = 'https://www.vulbox.com/board/internet/page/'
        self.freebuf_base_url = 'https://www.vulbox.com'
        self.events_id_list = self.events_id_read()
        self.key_word_list = self.key_words_read
        self.fileMd5 = self.file_md5_get
        self.html = 0
        # self.count = 0

    def __del__(self):
        print '漏洞盒子监看机器人 is shutdown'

    def data_request(self):
        """
        从漏洞盒子获取最新的10页事件
        返回一个存储网页的list
        """
        print 'freebuf_dataRequest'
        urls = []
        htmls = []
        for num in range(1, 11):
            urls.append(self.freebuf_url+'%s' % num)
        for url in urls:
            while True:
                try:
                    page = requests.get(url, timeout=30, verify=True)
                except requests.exceptions.ConnectTimeout:
                    time.sleep(60)
                    continue
                except requests.exceptions.ConnectionError:
                    time.sleep(30)
                    continue
                except requests.exceptions.HTTPError as e:
                    error_text = exception_format(get_current_function_name(), e)
                    self.send_text_email('Important Program Exception', error_text, 'ExceptionInfo')
                    time.sleep(600)
                    continue
                except Exception as e:
                    error_text = exception_format(get_current_function_name(), e)
                    self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
                    continue
                else:
                    if page.status_code == 200:
                        htmls.append(page.content)
                        # time.sleep(random.randint(0,60))
                        break
                    else:
                        error_text = "Page Code %s " % page.status_code
                        self.send_text_email('Page Error', error_text, 'ExceptionInfo')
                        continue
        return htmls

    def data_achieve(self, pages):
        """
        获取事件名和链接
        返回一个{链接:事件名}型的字典
        :param pages:
        """
        print 'freebuf_dataAchieve'
        events = {}
        for page in pages:
            while True:
                try:
                    soup = BeautifulSoup(page, "html5lib")
                except Exception as e:
                    error_text = exception_format(get_current_function_name(), e)
                    self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
                    self.data_request()
                else:
                    titles = soup.find_all(href=re.compile("/bugs/vulbox"), target="_blank")
                    for title in titles:
                        events[title['href']] = title.string.strip()
                    break
        return events

    def key_words_check(self, events):
        """
        检查获得的标题中是否含有要监看的关键字
        函数内调用sendRecord()
        没有返回值
        :param events:
        """
        print 'freebuf_keyWordscheck'
        tempfilemd5 = self.file_md5_check(self.fileMd5)
        if tempfilemd5:
            self.fileMd5 = tempfilemd5
            self.key_word_list = self.key_words_read
        try:
            for (freebuf_url, freebuf_title) in events.iteritems():
                # print freebuf_title
                for key1, values in self.key_word_list.iteritems():
                    if key1 in freebuf_title:
                        if values:
                            for value in values:
                                if value.get('KEY2') is not None:
                                    if value.get('KEY2') in freebuf_title:
                                        # print '1',freebuf_title
                                        self.send_record(freebuf_title, self.freebuf_base_url+freebuf_url,
                                                         freebuf_url.split('/')[-1])
                                    # else: #二级关键词不中的话继续查域名和内容
                                        # 2. 进入页面检查厂商域名
                                        # 3. 在页面内查找是否存在第二关键字
                                elif value.get('KEY2') is None:
                                    # print '3',freebuf_title
                                    self.send_record(freebuf_title, self.freebuf_base_url + freebuf_url,
                                                     freebuf_url.split('/')[-1])
                        else:
                            # print '2',freebuf_title
                            self.send_record(freebuf_title, self.freebuf_base_url+freebuf_url,
                                             freebuf_url.split('/')[-1])
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')

    def send_record(self, event_title, event_id, event_url):
        """
        调用邮件发送函数并记录被发送的事件ID
        没有返回值
        函数内调用sendTextEmail()
        :param event_id:
        :param event_url:
        :param event_title:
        """
        print 'freebuf_sendRecord'
        check_result = self.events_id_check(event_id, self.events_id_list)
        if 0 not in check_result:
            try:
                # pass #test to use
                self.send_text_email(event_title, event_url, 'securityInfo')
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                print error_text
            else:
                self.events_id_list.append(event_id)
                self.events_id_add(event_id)
        else:
            print event_title, " Same thing was sent,did not send same mail to everyone"


if __name__ == '__main__':

    robot = FreeBuf('keyWords.txt', '../Events/EventsIDfreebuf.txt')
    robot.key_words_check(robot.data_achieve(robot.data_request()))
