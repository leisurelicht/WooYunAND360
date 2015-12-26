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


class FixSky(filehandle.FileHandle, mail.MailCreate):
    """docstring for fix360"""
    def __init__(self, keys_file, events_id_file):
        super(FixSky, self).__init__('360补天监看机器人', keys_file, events_id_file)
        self._360fix_url = 'http://loudong.360.cn/vul/list'
        self._360base_url = 'http://loudong.360.cn'
        self.events_id_list = self.events_id_read()
        self.key_word_list = self.key_words_read
        self.fileMd5 = self.file_md5_get
        self.html = 0
        self.count = 0

    def __del__(self):
        print '360监看机器人 is shutdown'

    def data_request(self):
        """
        从360补天获取最新的10页事件
        返回一个存储网页的list
        """
        print '360_dataRequest'
        urls = []
        htmls = []
        for num in range(1, 11):
            urls.append(self._360fix_url + '/page/%s' % num)
        for url in urls:
            while True:
                try:
                    page = requests.get(url, timeout=30)
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
                        htmls.append(page.content)  # get page content
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
        print '360_dataAchieve'
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
                    titles = soup.find_all(href=re.compile("/vul/info/qid"))
                    # title2 = soup.find_all(href=re.compile("/company/info/id/"))
                    # title3 = soup.find_all(href=re.compile("/vul/search/"))
                    # titles = title1 + title2 +title3
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
        print '360_key_words_check'
        temp_file_md5 = self.file_md5_check(self.fileMd5)
        if temp_file_md5:
            self.fileMd5 = temp_file_md5
            self.key_word_list = self.key_words_read
        try:
            for (_360url, _360title) in events.iteritems():
                # print _360title
                for key1, values in self.key_word_list.iteritems():
                    if key1 in _360title:
                        if values:
                            for value in values:
                                # 1. 检查第二关键字是否存在
                                if value.get('KEY2') is not None:
                                    if value.get('KEY2') in _360title:
                                        # print '1.',_360title
                                        self.send_record(_360title, self._360base_url + _360url, _360url.split('/')[-1])
                                    # else: #二级关键词不中的话继续查域名和内容
                                        # 2. 进入页面检查厂商域名
                                        # 3. 在页面内查找是否存在第二关键字
                                elif value.get('KEY2') is None:
                                    # print '3.',_360title
                                    self.send_record(_360title, self._360base_url + _360url, _360url.split('/')[-1])
                        else:
                            # print '2.',_360title
                            self.send_record(_360title, self._360base_url + _360url, _360url.split('/')[-1])
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')

    def send_record(self, event_title, event_url, event_id):
        """
        调用邮件发送函数并记录被发送的事件ID
        没有返回值
        函数内调用sendTextEmail()
        :param event_id:
        :param event_url:
        :param event_title:
        """
        print '360_sendRecord'
        check_result = self.events_id_check(event_id, self.events_id_list)
        if 0 not in check_result:
            try:
                # pass #test to use
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
    robot = FixSky('../Config/keyWords.txt', '../Events/EventsID360.txt')
    robot.key_words_check(robot.data_achieve(robot.data_request()))