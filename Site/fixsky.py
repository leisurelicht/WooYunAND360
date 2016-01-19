#! usr/bin/env python
# -*- coding=utf-8 -*-
import re
import logging
from lxml import etree
from bs4 import BeautifulSoup
from Common import mail, filehandle
from Common.common import *

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()


class FixSky(filehandle.FileHandle, mail.MailCreate):
    """docstring for fix360"""
    def __init__(self, keys_file, events_id_file):
        super(FixSky, self).__init__('启明360补天监看机器人', keys_file, events_id_file)
        self.url = 'http://loudong.360.cn/vul/list'
        self._360base_url = 'http://loudong.360.cn'
        self.events_id_list = self.events_id_read()
        self.key_words_list = self.key_words_read
        self.fileMd5 = self.file_md5_get
        self.html = 0
        self.count = 0

        self.headers = {
            'Host': 'loudong.360.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Referer': 'http://loudong.360.cn/vul/list',
            'Cookie': 'pgv_pvi=6038021120; PHPSESSID=6d947f3863a63879a26bd9bcf9d6804e; \
            CNZZDATA1254945139=1429258137-1453105216-%7C1453105216; IESESSION=alive; \
            tencentSig=1869615104; pgv_si=s9109886976; __guid=90162694.2437595648188995600.1453105662014.9954; \
            Q=u%3D%25P4%25ON%25O3%25OS_001%26n%3D%25P4%25ON%25P1%25R3%25PP%25RP%25O3%25OS%26le%3DZmLlBQL0AGHjWGDjpKRhL29g%26m%3D%26qid%3D101635689%26im%3D1_t01e12f28b905f7e221%26src%3Dpcw_webscan%26t%3D1; \
            T=s%3D4dc5ac3aa810648d687e84144622f1be%26t%3D1453105664%26lm%3D%26lf%3D1%26sk%3D2cbe34b8bcf6ae343f239584234e7b61%26mt%3D1453105664%26rc%3D%26v%3D2.0%26a%3D1',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }

        #self.con = database.connect_fixsky()

    def __del__(self):
        print '360监看机器人 is shutdown'

    def data_achieve(self, pages):
        """
        获取事件名和链接
        返回一个{链接:事件名}型的字典
        :param pages:
        """
        print '360_dataAchieve'
        events = {}
        for page in pages:
            try:
                soup = BeautifulSoup(page, "html5lib")
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
            else:
                titles = soup.find_all(href=re.compile("/vul/info/qid"))
                # title2 = soup.find_all(href=re.compile("/company/info/id/"))
                # title3 = soup.find_all(href=re.compile("/vul/search/"))
                # titles = title1 + title2 +title3
                for title in titles:
                    events[title['href']] = title.string.strip()
                    break
        # database.remove_date(self.con)
        # database.insert_data(self.con, data)
        return events

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
            # self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
        else:
            des = soup.find(id="ld_td_description").string  # 获取描述
            dom_exi = soup.find(class_="ld-vul-v1-tips").string
            if u'已注册' in dom_exi:
                url2 = soup.find(href=re.compile(u'/vul/search/c/'))['href']
                dom_page = self.request(self._360base_url+url2, self.headers)
                raw_dom = etree.HTML(dom_page.content)
                print raw_dom.xpath('/html/head/title')[0]
                print raw_dom.xpath('/html/body/div[2]/div/div/div[1]/div[2]/table/tbody/tr[1]/td[1]')


            # if url2:
            #     page = self.data_request(url=url2, header=self.headers).content
            #     if page:
            #         raw_domain = etree.HTML(page)
            #         if u"厂商信息" in unicode(raw_domain.xpath('/html/head/title/text()')[0]):
            #             domain = get_tld(''.join(list(raw_domain.xpath('/html/body/div[5]/h3[1]/text()')[0])[3:]))
            #             return domain, des
            #         else:
            #         # if '厂商' in sign and '不存在' in sign and '未通过审核' in sign:
            #             return None, des
            #     else:
            #         return None, des
            # else:
            #     return None, des

    def key_words_check(self, events):
        """
        检查获得的标题中是否含有要监看的关键字
        函数内调用sendRecord()
        没有返回值
        :param events:
        """
        print '360_key_words_check'
        md5value = self.file_md5_get
        if md5value != self.fileMd5:
            self.key_words_list = self.key_words_read
            self.fileMd5 = md5value
        try:
            for (_360url, _360title) in events.iteritems():
                _360title = _360title.lower()
                print _360title
                for key1, values in self.key_words_list.iteritems():
                    if key1 in _360title:
                        if values:
                            for value in values:
                                # 1. 检查第二关键字是否存在
                                if value.get('KEY2'):
                                    if value.get('KEY2') in _360title:
                                        # print '1.',_360title
                                        self.send_record(_360title,
                                                         self._360base_url + _360url,
                                                         _360url.split('/')[-1])
                                    # else: #二级关键词不中的话继续查域名和内容
                                        # 2. 进入页面检查厂商域名
                                        # 3. 在页面内查找是否存在第二关键字
                                elif value.get('KEY2') is None:
                                    # print '3.',_360title
                                    self.send_record(_360title,
                                                     self._360base_url + _360url,
                                                     _360url.split('/')[-1])
                        else:
                            # print '2.',_360title
                            self.send_record(_360title,
                                             self._360base_url + _360url,
                                             _360url.split('/')[-1])
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')


if __name__ == '__main__':
    robot = FixSky('../Config/keyWords.txt', '../Events/EventsID360.txt')
    # robot.key_words_check(robot.data_achieve(robot.data_request()))
    # robot.domain_description_achieve('http://loudong.360.cn/vul/info/qid/QTVA-2016-366149')
    robot.domain_description_achieve('http://loudong.360.cn/vul/info/qid/QTVA-2016-365585')
