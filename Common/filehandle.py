#! usr/bin/env python
# -*- coding=utf-8 -*-

import os
import json
import logging
import hashlib
import requests
import time
import mail
import random
from tld import get_tld
from common import *

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()


class FileHandle(mail.MailCreate):
    """docstring for FileHandle"""

    def __init__(self, sender_name, keys_file, events_id_file):
        super(FileHandle, self).__init__(sender_name)
        self.key_file = keys_file
        self.events_Id_file = events_id_file
        self.url = None  # 在子类初始化
        self.events_id_list = []  # 在子类初始化

    def request(self, url, header=None):
        """

        :param header:
        :param url:
        :return:
        """
        print 'request'
        count = 0
        while True:
            try:
                if count > 3:
                    return None
                page = requests.get(url=url, headers=header, timeout=30,  verify=True)
            except requests.exceptions.ConnectTimeout:
                time.sleep(60)
                count += 1
                continue
            except requests.exceptions.ConnectionError:
                time.sleep(30)
                count += 1
                continue
            except requests.exceptions.HTTPError as e:
                error_text = exception_format(get_current_function_name(), e)
                count += 1
                self.send_text_email('Important Program Exception', error_text, 'ExceptionInfo')
                time.sleep(600)
                continue
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                count += 1
                print error_text
                self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
                continue
            else:
                if page.status_code == 200:
                    return page  # get page
                    # time.sleep(random.randint(0,60))
                else:
                    error_text = "Page Code %s " % page.status_code
                    count += 1
                    self.send_text_email('Page Error', error_text, 'ExceptionInfo')
                    continue

    def page_request(self):
        """
        获取最新的10页事件
        返回一个存储网页的list
        """
        print 'data_Request'
        urls = []
        htmls = []
        for num in range(1, 11):
            urls.append(self.url + '/page/%s' % num)
        for url in urls:
            htmls.append(self.request(url).content)
            time.sleep(random.randint(1,5))
        return htmls

    @staticmethod
    def get_domain(url):
        """
        获取域名
        :param url:
        :return:
        """
        print "domain_get"
        return get_tld(url)

    def events_id_read(self):
        """
        从文件中读取已经发送过邮件的事件ID
        返回一个list
        """
        print "events_id_read"
        error_id = []
        if os.path.exists(self.events_Id_file):
            with open(self.events_Id_file) as errors:
                for error in errors:
                    if not error.isspace():
                        error_id.append(error.strip())
            return error_id
        else:
            file_path, file_name = os.path.split(self.events_Id_file)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            else:
                tmp = open(self.events_Id_file, 'a')
                tmp.close()

    @staticmethod
    def events_id_check(new_id, events_id_list):
        """
        通过ID确定事件是否已经被发送过
        返回一个list
        如果list里包含0,则已被发送过
        :param new_id: 新事件的ID
        :param events_id_list: 事件的ID集合
        """
        print 'events_id_check'
        temp = []
        if len(events_id_list) > 0:
            for eventId in events_id_list:
                if not eventId.isspace():
                    temp.append(cmp(eventId, new_id))
        return temp

    def events_id_add(self, new_id):
        """
        向EventsID.txt文件中加入一个事件ID
        :param new_id: 事件ID
        """
        tmp = open(self.events_Id_file, 'a')
        tmp.write(new_id + '\n')
        tmp.close()

    @property
    def key_words_read(self):
        """
        从文件中读取需要监看的关键字
        返回一个json格式的数据
        """
        print 'key_words_read'
        if os.path.exists(self.key_file):
            with open(self.key_file) as keys:
                tmp = keys.read()
            try:
                keywordslist = json.loads(tmp)
            except (AttributeError, ValueError):
                error_text = "请检查关键词文件格式是否正确"
                print error_text
                self.send_text_email("Program Exception", error_text, "ExceptionInfo")
                exit(0)
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                print error_text
                self.send_text_email("Program Exception", error_text, "ExceptionInfo")
            else:
                # print keywordslist
                return keywordslist

        else:
            print "关键词监看文件不存在"
            tmp = open(self.key_file, 'a')
            tmp.close()

    @property
    def file_md5_get(self):
        """
        获取文件的MD5值
        返回一个MD5值
        """
        print 'file_md5_get'
        try:
            file_md5 = hashlib.md5()
            with open(self.key_file) as file_temp:
                file_md5.update(file_temp.read().strip())
                md5temp = file_md5.hexdigest()
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            self.send_text_email("Program Exception", error_text, "ExceptionInfo")
        else:
            return md5temp

    def send_record(self, event_title, event_url, event_id, keyword_tag):  # tag
        """
        调用邮件发送函数并记录被发送的事件ID
        没有返回值
        函数内调用sendTextEmail()
        :param event_id:
        :param event_url:
        :param event_title:
        """
        check_result = self.events_id_check(event_id, self.events_id_list)
        if 0 not in check_result:
            try:
                self.receiver_get(keyword_tag)
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
    test = FileHandle('filehandle', '../Config/KeyWords.txt', '../Events/EventsID360.txt')
    # print test.eventsIdread()
    # for key in test.key_words_read():
    #    print key
    # a=test.file_md5_get()
    # print a

    # while True:
    #    b=test.file_md5_check(a)
    #    print b
    #    if b:
    #        a = b
    #    time.sleep(5)
    a=test.key_words_read()
