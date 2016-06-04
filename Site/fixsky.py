#! usr/bin/env python
# -*- coding=utf-8 -*-
import re
import logging
from bs4 import BeautifulSoup
from Common import mail, filehandle, database
from Common.common import exception_format, get_current_function_name

# reload(sys)
# sys.setdefaultencoding('utf8')
logging.basicConfig()


class FixSky(filehandle.FileHandle, mail.MailCreate):
    """docstring for fix360"""
    def __init__(self, keys_file, events_id_file):
        super(FixSky, self).__init__('启明360补天监看机器人', keys_file, events_id_file)
        self.url = 'http://loudong.360.cn/vul/list'
        self._360base_url = 'http://loudong.360.cn'
        # self.events_id_list = self.events_id_read
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
            'Cookie': 'tencentSig=7366209536; tencentSig=1638778880; PHPSESSID=c25719d3b3c6aad81592cd67faa78386; IESESSION=alive; CNZZDATA1254945139=1259737161-1455975761-http%253A%252F%252Floudong.360.cn%252F%7C1455981502; __guid=90162694.4484595771534412000.1455981177447.6384; pgv_pvi=4550801408; pgv_si=s3499901952; quCryptCode=Mhl7mCCsuvA%252FTZksdDAzBWN29MvW0Ad5835Wu%252FxXaRtlXDlMUzQv3Q%252FfFXMbGEsuKBix2qiTP%252FI%253D; quCapStyle=2; Q=u%3D%25P4%25ON%25O3%25OS_001%26n%3D%25P4%25ON%25P1%25R3%25PP%25RP%25O3%25OS%26le%3DZmLlBQL0AGHjWGDjpKRhL29g%26m%3D%26qid%3D101635689%26im%3D1_t01e12f28b905f7e221%26src%3Dpcw_webscan%26t%3D1; T=s%3Dd004b8db2a979f1e855714db3d60b72f%26t%3D1455983195%26lm%3D%26lf%3D1%26sk%3D132e01b83a77e9b35ae247d533d4e118%26mt%3D1455983195%26rc%3D%26v%3D2.0%26a%3D1',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }

        # self.con = database.connect_fixsky()

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
        data = []
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
                    events['link'] = title['href']
                    events['title'] = title.string.strip()
                    data.append(events.copy())
                continue
        # database.remove_date(self.con)
        # database.insert_data(self.con, data)
        return data

    def domain_description_achieve(self, url):
        """
        获取360补天事件页面中的描述部分和厂商域名
        :param url: 360补天漏洞事件页面
        :return: （domain,description）domain可能为None, description可能为''
        """
        print '360_domain_description_achieve'
        page = self.request(url=url, header=self.headers)
        if page:
            page = page.content
        try:
            soup = BeautifulSoup(page, "html5lib")
            des = soup.find(id="ld_td_description").string  # 获取描述
            dom_exi = soup.find(class_="ld-vul-v1-tips").string
            if u'已注册' in dom_exi:
                url2 = soup.find(href=re.compile(u'/vul/search/c/'))['href']
                dom_page = self.request(self._360base_url+url2, self.headers)
                print "dom_page",dom_page
                if dom_page:
                    print 'url:',dom_page.url
                    raw_dom = BeautifulSoup(dom_page.content, "html5lib")
                    tmp = raw_dom.find('div',class_='company_info') #360有反机器人机制
                    if tmp:
                        domain = tmp.table.tbody.tr.td.next_sibling.next_sibling.string
                        print 'domain:',domain
                        return domain, des
                    else:
                        return None,des
                else:
                    return None, des
            else:
                return None, des
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            print error_text
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')
            return None, None

    def key_words_check(self, data):
        """
        检查获得的标题中是否含有要监看的关键字
        函数内调用sendRecord()
        没有返回值
        :param data:
        """
        print '360_key_words_check'
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
                            dom, des = self.domain_description_achieve(self._360base_url+detail.get('link'))
                            for value in values:
                                if value.get('KEY2'):
                                    # 1. 检查第二关键字是否存在标题中
                                    if value.get('KEY2') in title:
                                        # print '1.',_360title
                                        self.send_record(detail.get('title'),
                                                         self._360base_url + detail.get('link'),
                                                         detail.get('link').split('/')[-1],
                                                         value.get('TAG'))
                                    # 1. 检查第二关键字是否存在描述中
                                    elif des and (value.get('KEY2') in des):
                                        self.send_record(detail.get('title'),
                                                         self._360base_url + detail.get('link'),
                                                         detail.get('link').split('/')[-1],
                                                         value.get('TAG'))
                                elif value.get('URL') and dom and (value.get('URL') in dom):
                                    # print '3.',_360title
                                    self.send_record(detail.get('title'),
                                                     self._360base_url + detail.get('link'),
                                                     detail.get('link').split('/')[-1],
                                                     value.get('TAG'))
                                else:
                                    continue
                        else:
                            # print '2.',_360title
                            self.send_record(detail.get('title'),
                                             self._360base_url + detail.get('link'),
                                             detail.get('link').split('/')[-1],
                                             value.get('TAG'))
                    else:
                        print "事件标题中不存在监看关键词『", key1, "』开始检测下一关键词"
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            self.send_text_email('Program Exception', error_text, 'ExceptionInfo')


if __name__ == '__main__':
    robot = FixSky('../Config/keyWords.txt', '../Events/EventsID360.txt')
    # print robot.data_achieve(robot.page_request())
    robot.key_words_check(robot.data_achieve(robot.page_request()))
    # robot.domain_description_achieve('http://loudong.360.cn/vul/info/qid/QTVA-2016-366149')
    # robot.domain_description_achieve('http://loudong.360.cn/vul/info/qid/QTVA-2016-367457')
