#! usr/bin/env python
# -*- coding=utf-8 -*-
import sys
import time
import smtplib
import ConfigParser
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from common import *

reload(sys)
sys.setdefaultencoding('utf8')


class MailCreate(object):
    """
    邮件类
    """

    def __init__(self, sender_name):
        """
        sender : 邮件来源名
        :type sender_name: wooyun,360或漏洞盒子
        """
        super(MailCreate, self).__init__()
        self.mailName = sender_name
        self.count = 0  # 邮箱认证尝试连接次数,超过3次则更换邮箱
        self.Mail = 'MailOne'
        self.Mail_choose = True
        self.smtp_server = '0'
        self.smtp_server_port = '0'
        self.sender = '0'
        self.receiver = []
        self.receiver_admin = '0'
        self.username = '0'
        self.password = '0'
        try:
            self.config = ConfigParser.ConfigParser()
            self.address = ConfigParser.ConfigParser()
            self.config.read("../Config/mailconfig.ini")
            self.address.read("../Config/mail_address.ini")
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            print error_text
        self.mail_init()  # mailInit函数只在此处被调用

    # @staticmethod
    # def _format_address(s):
    #     """
    #     格式化一个邮件地址
    #     返回一个被格式化为 '别名<email address>' 的邮件地址
    #     """
    #     # if isinstance(s, unicode):
    #     #     name, address = parseaddr(s)
    #     #     return formataddr((Header(name, 'utf-8').encode(),
    #     #                        address.encode('utf-8') if isinstance(address, unicode) else address))
    #     # elif isinstance(s, list):
    #     #     add_list = []
    #     #     # name = unicode(name)
    #     #     for address in s:
    #     #         add_list.append(formataddr((Header(name, 'utf-8').encode(),
    #     #                                     address.encode('utf-8') if isinstance(address, unicode) else address)))
    #     #     return ','.join(add_list)
    #     name, address = parseaddr(s)
    #     return formataddr((Header(name, 'utf-8').encode(),address.encode('utf-8') if isinstance(address, unicode) else address))

    def _format_addr(self,s):
        '''
        格式化一个邮件地址
        返回一个被格式化为 '别名<email address>' 的邮件地址
        '''
        name , addr = parseaddr(s)
        return formataddr(( Header(name,'utf-8').encode(),\
                          addr.encode('utf-8') if isinstance(addr,unicode) else addr ))

    def _format_address_list(self,s):
        add_list = []
        # name = unicode(name)
        for address in s:
            add_list.append(formataddr((Header('', 'utf-8').encode(),
                                        address.encode('utf-8') if isinstance(address, unicode) else address)))
        return ','.join(add_list)


    def mail_init(self):
        """
        初始化邮件设置
        返回邮件的参数
        """
        print "『" + 'mail_init' + "』\n" + "『邮箱初始化开始』"
        if self.Mail_choose:
            self.Mail = 'MailOne'
        else:
            self.Mail = 'MailTwo'
        try:
            self.smtp_server = self.config.get(self.Mail, 'SmtpServer').strip()
            self.smtp_server_port = self.config.get(self.Mail, "SmtpServer_Port").strip()
            self.sender = self.config.get(self.Mail, "SenderMail")
            self.username = self.config.get(self.Mail, "MailName").strip()
            self.password = self.config.get(self.Mail, "MailPassword").strip()
            self.receiver_admin = self.address.get('Admin_Address', "ReceiverMail_Admin").split(',')
        except ConfigParser.NoSectionError:
            print "*" * 34
            print "*" * 10, "邮箱未进行配置", "*" * 10
            print "*" * 34
            print "*" * 12, "程序退出", "*" * 13
            print "*" * 34
            exit(0)
        except Exception as e:
            error_text = exception_format(get_current_function_name(), e)
            print error_text
        else:
            print "『邮箱配置成功』"

    def receiver_get(self, keyword_tag):
        """
        根据keyword的tag获取相应的邮箱地址
        :param keyword_tag:KeyWords最后的TAG
        :return:
        """

        address_tag = self.address.items("User_Address")
        for tmp in address_tag:
            if str(keyword_tag) in tmp[1].split(','):
                self.receiver.append(tmp[0])
        # print 'receiver',self.receiver

    def send_text_email(self, title, message, message_type):
        """
        发送文本邮件
        没有返回值
        函数内调用_format_address()
        :param message_type:
        :param message:
        :param title:
        """
        print 'send_text_email %s ' % title
        msg = MIMEText(message, 'plain', 'utf-8')  # 中文参数‘utf-8’，单字节字符不需要
        msg['From'] = self._format_addr(u'%s<%s>' % (self.mailName, self.sender))
        msg['Subject'] = Header(title)
        while 1:
            try:
                smtp = smtplib.SMTP()
                # smtp.set_debuglevel(1)
                print '开始尝试连接邮箱'
                smtp.connect(self.smtp_server, self.smtp_server_port)
                print '成功连接邮箱'
                print '开始尝试登陆邮箱'
                smtp.login(self.username, self.password)
                print '成功登陆邮箱'
                if message_type == "securityInfo":
                    print '开始发送事件邮件'
                    msg[ 'To' ] = self._format_addr(u'Dollars<%s> ' % ','.join(self.receiver) )
                    # 这里有receiver为多个人时无法正确被格式化.
                    # ','join(self.receiver)无法正确格式化,貌似是%s长度有限制
                    # ''.join(self.receiver)只能格式化第一个邮箱地址
                    smtp.sendmail( self.sender , self.receiver , msg.as_string() )
                    print '成功发送事件邮件'
                    print '成功发送事件邮件'
                elif message_type == "ExceptionInfo":
                    print '开始发送问题邮件'
                    msg[ 'To' ] = self._format_addr(u'Admin<%s>' % ','.join(self.receiver_admin) )
                    smtp.sendmail( self.sender , self.receiver_admin , msg.as_string() )
                    print '成功发送问题邮件'
                elif message_type == "time_report":
                    print '开始发送运行报告邮件'
                    msg[ 'To' ] = self._format_addr(u'Admin<%s>' % ','.join(self.receiver_admin) )
                    smtp.sendmail( self.sender , self.receiver_admin , msg.as_string() )
                    print '成功发送运行报告邮件'
            except smtplib.SMTPAuthenticationError:
                print '认证失败,邮箱连接可能出问题了'
                self.count += 1
                if self.count < 3:
                    time.sleep(10)
                    continue
                else:
                    print '更换邮箱后重试...'
                    self.Mail_choose = not self.Mail_choose
                    self.mail_init()
                    self.count = 0
                    continue
            except Exception as e:
                error_text = exception_format(get_current_function_name(), e)
                print error_text
                time.sleep(10)
                continue
            else:
                smtp.quit()
                self.count = 0
                break

if __name__ == '__main__':
    test = MailCreate('测试机器人')
    test.receiver_get(5)
    #test.send_text_email("test", 'info', "securityInfo")

    test.send_text_email("except", 'bad', "ExceptionInfo")
    # test.send_text_email("time",'time report',"time_report")
    #
    # test2 = mail('测试机器人')
    # while True:
    # test2.send_text_email("test",'test message',"securityInfo")
    # time.sleep(5)
