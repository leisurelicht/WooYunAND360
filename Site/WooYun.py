#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import time
import socket
import logging
from lxml import etree
from bs4 import BeautifulSoup
from Common import mail, filehandle, database
from Common.common import exception_format, get_current_function_name

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()


class WooYun(filehandle.FileHandle, mail.MailCreate):
    """docstring for WooYun"""

    def __init__(self, keys_file, events_id_file):
        super(WooYun, self).__init__('启明WooYun监看机器人', keys_file, events_id_file)
        self.wooyun_url = 'http://api.wooyun.org/bugs/submit'
        self.events_id_list = self.events_id_read()
        self.key_words_list = self.key_words_read
        self.fileMd5 = self.file_md5_get
        socket.setdefaulttimeout = 30
        self.count = 0
        self.headers = {
            'Host': 'www.wooyun.org',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Referer': 'http://www.wooyun.org/index.php',
            'Connection': 'keep-alive'
        }
        # self.con = database.connect_wooyun()

    def __del__(self):
        print 'WooYun监看机器人 is shutdown'

    def api_request(self, url=None, header=None):
        """
        从乌云API获取json格式的数据
        返回json格式的数据
        :param header:
        :param url:
        """
        print 'WooYun_dataRequest'
        url = url or self.wooyun_url
        while True:
            try:
                if self.count > 10:
                    self.send_text_email('Important Program Exception', 'Target url can not reach', 'ExceptionInfo')
                    self.count = 0
                    return None
                page = requests.get(url, timeout=30, headers=header)
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
            except requests.exceptions.ConnectionError:  # 调试时连不上多半是这个问题
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
                if page.status_code == 200:
                    self.count = 0
                    return page
                elif page.status_code == 522:
                    continue
                elif page.status_code == 504:
                    time.sleep(30)
                    self.count += 1
                    continue
                elif page.status_code == 503:
                    if page.headers.get('Retry-After'):
                        time.sleep(int(page.headers.get('Retry-After')))
                    else:
                        pass
                    self.count += 1
                    continue
                else:
                    error_text = "Page Code %s " % page.status_code
                    self.send_text_email('Page Error', error_text, 'ExceptionInfo')
                    self.count += 1
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
                text = self.page_request()
            else:
                # database.remove_date(self.con)
                # database.insert_data(self.con, data)
                return data

    def domain_description_achieve(self, url):
        """
        获取WooYun事件页面中的描述部分和厂商域名
        :param url: wooyun漏洞页面
        :return: （domain,description）domain可能为None, description可能为''
        """
        print 'WooYun_domain_description_achieve'
        page = self.request(url=url, header=self.headers).content
        try:
            soup = BeautifulSoup(page, "html5lib")
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            print error_text
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
        else:
            des = soup.find(class_="detail wybug_description").string  # 获取描述
            url2 = soup.find('h3', class_="wybug_corp").a['href']
            if url2:
                page = self.request(url=url2, header=self.headers).content
                if page:
                    raw_domain = etree.HTML(page)
                    if u"厂商信息" in unicode(raw_domain.xpath('/html/head/title/text()')[0]):
                        domain = self.get_domain(''.join(list(raw_domain.xpath('/html/body/div[5]/h3[1]/text()')[0])[3:]))
                        return domain, des  # 域名, 描述
                    else:
                        # if '厂商' in sign and '不存在' in sign and '未通过审核' in sign:
                        return None, des
                else:
                    return None, des
            else:
                return None, des

    def key_words_check(self, data):
        """
        检查获得的标题中是否含有要监看的关键字
        内部调用sendRecord()
        没有返回值
        :param data: 事件标题组成的list
        """
        print 'WooYun_key_words_check'
        md5value = self.file_md5_get
        if md5value != self.fileMd5:
            self.key_words_list = self.key_words_read
            self.fileMd5 = md5value
        try:
            for detail in data:
                title = detail.get('title').lower()
                print title
                for key1, values in self.key_words_list.iteritems():
                    if key1 in title:
                        if values:
                            dom, des = self.domain_description_achieve(detail.get('link'))
                            for value in values:
                                if value.get('KEY2'):
                                    if value.get('KEY2') in title:
                                        # 1. 在title中继续检查第二关键字是否存在
                                        self.send_record(detail.get('title').strip(),
                                                         detail.get('link'),
                                                         detail.get('id'),
                                                         value.get('TAG'))
                                    elif des and (value.get('KEY2') in des):
                                        # 2. 在事件描述中查找是否存在第二关键字
                                        self.send_record(detail.get('title').strip(),
                                                         detail.get('link'),
                                                         detail.get('id'),
                                                         value.get('TAG'))
                                elif value.get('URL') and dom and (value.get('URL') in dom):
                                    # 二级关键词不中的话继续查域名
                                    # 3. 进入页面检查厂商域名
                                    self.send_record(detail.get('title').strip(),
                                                     detail.get('link'),
                                                     detail.get('id'),
                                                     value.get('TAG'))
                                # elif value.get('KEY2') is None and value.get('URL') is not None:
                                #     # 会减少因域名导致的漏报,但也会增加误报
                                #     self.send_record(detail.get('title').strip(),
                                #                          detail.get('link'),
                                #                          detail.get('id'))
                                else:
                                    # 不存在二级关键词和域名的情况下,这就是中了嘛.
                                    self.send_record(detail.get('title').strip(),
                                             detail.get('link'),
                                             detail.get('id'),
                                             value.get('TAG'))
                        else:
                            pass


                    else:
                        print "事件标题中不存在监看关键词『", key1, "』,开始检测下一关键词"
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            print error_text
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
if __name__ == 'WooYun':
    pass
elif __name__ == '__main__':
    robot_WooYun = WooYun('../Config/KeyWords.txt', '../Events/EventsID.txt')
    # tmp = robot_WooYun.api_request()
    # print tmp.headers.get('Set-Cookie')
    # robot_WooYun.data_achieve(robot_WooYun.api_request())
    robot_WooYun.key_words_check(robot_WooYun.data_achieve(robot_WooYun.api_request()))
    # dom, des = robot_WooYun.domain_description_achieve('http://www.wooyun.org/bugs/wooyun-2015-0163298')
    # print dom
    # print des