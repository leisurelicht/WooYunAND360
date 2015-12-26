#! usr/bin/env python
# -*- coding=utf-8 -*-
import os
import json
import logging
import hashlib
import mail
from common import *

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()


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


class FileHandle(mail.MailCreate):
    """docstring for FileHandle"""

    def __init__(self, sender_name, keys_file, events_id_file):
        super(FileHandle, self).__init__(sender_name)
        self.key_file = keys_file
        self.events_Id_file = events_id_file

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
            except Exception as e:
                error_text = exception_format(e)
                self.sendTextEmail("Program Exception", error_text, "ExceptionInfo")
            else:
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
            with open(self.key_file) as filetemp:
                file_md5.update(filetemp.read().strip())
                md5temp = file_md5.hexdigest()
        except Exception as e:
            error_text = exception_format(e)
            self.sendTextEmail("Program Exception", error_text, "ExceptionInfo")
        else:
            return md5temp

    def file_md5_check(self, old_file_md5):
        """
        检查文件的MD5值,确定文件是否发生改变
        没有发生改变返回False
        发生改变返回新的MD5值
        :param old_file_md5:
        """
        print 'file_md5_check'
        try:
            # filemd5 = hashlib.md5()
            # with open(self.keyfile) as filetemp:
            #    filemd5.update( filetemp.read().strip() )
            #    md5temp = filemd5.hexdigest()
            md5temp = self.file_md5_get()
        except Exception as e:
            error_text = exception_format(e)
            self.sendTextEmail("Program Exception", error_text, "ExceptionInfo")
        else:
            if old_file_md5 == md5temp:
                return False
            else:
                return md5temp
        return False

if __name__ == '__main__':
    test = FileHandle('filehandle', 'KeyWords.txt', '../Events/EventsID360.txt')
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
    print test.events_id_read()
