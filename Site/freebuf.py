#! usr/bin/env python
# -*- coding=utf-8 -*-


import logging
from bs4 import BeautifulSoup
from Common import mail, filehandle
from Common.common import exception_format, get_current_function_name

# reload(sys)
# sys.setdefaultencoding('utf8')
logging.basicConfig()


class FreeBuf(filehandle.FileHandle, mail.MailCreate):
    """docstring for FreeBuf"""
    def __init__(self, keys_file, events_id_file):
        super(FreeBuf, self).__init__('启明漏洞盒子监看机器人', keys_file, events_id_file)
        self.url = 'https://www.vulbox.com/board/internet/page/'
        self.freebuf_base_url = 'https://www.vulbox.com'
        # self.events_id_list = self.events_id_read
        self.key_words_list = self.key_words_read
        self.fileMd5 = self.file_md5_get
        self.html = 0
        # self.count = 0

    def __del__(self):
        print '漏洞盒子监看机器人 is shutdown'

    def data_achieve(self, pages):
        """
        获取事件名和链接
        返回一个{链接:事件名}型的字典
        :param pages:
        """
        print 'freebuf_dataAchieve'
        events = {}
        data = []
        for page in pages:
            try:
                soup = BeautifulSoup(page, "html5lib")
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
            else:
                #titles = soup.find_all('a',href=re.compile("/bugs/vulbox"), target="_blank")
                titles = soup.find_all('h4',class_='tit')
                for title in titles:
                    events['link'] = title.a['href']
                    events['title'] = title.a.string.strip()
                    data.append(events.copy())
                continue
        # database.remove_date(self.con)
        # database.insert_data(self.con, data)
        return data

    def key_words_check(self, events):
        """
        检查获得的标题中是否含有要监看的关键字
        函数内调用sendRecord()
        没有返回值
        :param events:
        """
        print 'freebuf_keyWords_check'
        md5value = self.file_md5_get
        if md5value != self.fileMd5:
            self.key_words_list = self.key_words_read
            self.fileMd5 = md5value
        try:
            for detail in events:
                title = detail.get('title').lower()
                print title
                for key1, values in self.key_words_list.iteritems():
                    if key1 in title:
                        if values:
                            for value in values:
                                if value.get('KEY2') is not None:
                                    if value.get('KEY2') in title:
                                        self.send_record(detail.get('title'),
                                                         self.freebuf_base_url + detail.get('link'),
                                                         detail.get('link').split('/')[-1],
                                                         value.get('TAG'))
                                    # else: #二级关键词不中的话继续查域名和内容
                                        # 2. 进入页面检查厂商域名
                                        # 3. 在页面内查找是否存在第二关键字
                                        # 页面不是很规律,有点麻烦
                                elif value.get('KEY2') is None:
                                    self.send_record(detail.get('title'),
                                                     self.freebuf_base_url + detail.get('link'),
                                                     detail.get('link').split('/')[-1],
                                                     value.get('TAG'))
                        else:
                            self.send_record(detail.get('title'),
                                             self.freebuf_base_url + detail.get('link'),
                                             detail.get('link').split('/')[-1],
                                             value.get('TAG'))
                    else:
                        print "事件标题中不存在监看关键词『", key1, "』开始检测下一关键词"
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')


if __name__ == '__main__':

    robot = FreeBuf('../Config/keyWords.txt', '../Events/EventsIDfreebuf.txt')
    robot.data_achieve(robot.page_request())
    robot.key_words_check(robot.data_achieve(robot.page_request()))
