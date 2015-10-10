#! usr/bin/env python
#-*- coding=utf-8 -*-

import sys
import time
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr , formataddr
from ConfigParser import ConfigParser



reload(sys)
sys.setdefaultencoding('utf8')
#logging.basicConfig()


class MailCreate(object):
    """
    邮件类
    """
    def __init__(self,sendername):
        '''
        sender : 邮件来源名
        '''
        super(MailCreate, self).__init__()
        self.mailName = sendername
        self.count = 0 #邮箱认证尝试连接次数,超过3次则更换邮箱
        self.Mail = 'MailOne'
        self.Mailchoose = True
        try:
            self.config = ConfigParser()
            self.config.read( 'mailconfig.ini' )
        except Exception as e :
            raise e
        self.mailInit() #mailInit函数只在此处被调用

    def _format_addr(self,s):
        '''
        格式化一个邮件地址
        返回一个被格式化为 '别名<email address>' 的邮件地址
        '''
        name , addr = parseaddr(s)
        return formataddr(( Header(name,'utf-8').encode(),\
                          addr.encode('utf-8') if isinstance(addr,unicode) else addr ))

    def mailInit(self):
        """
        初始化邮件设置
        返回邮件的参数
        """
        print 'mailInit'
        if self.Mailchoose:
            self.Mail == 'MailOne'
        else:
            self.Mail == 'MailTwo'
        #if( mailchoose == 'backup' ):
        #    if ( self.Mail == 'MailOne' ):
        #        self.Mail = 'MailTwo'
        #    elif ( self.Mail == 'MailTwo' ):
        #        self.Mail ='MailOne'

        try:
            self.smtpserver = self.config.get(self.Mail,"SmtpServer").strip()
            self.smtpserver_port = self.config.get(self.Mail,"SmtpServer_Port").strip()
            self.sender = self.config.get(self.Mail,"SenderMail")
            self.receiver = self.config.get(self.Mail,"ReceiverMail").split(',')
            self.receiver_admin = self.config.get(self.Mail,"ReceiverMail_Admin").split(',')
            self.username = self.config.get(self.Mail,"MailName").strip()
            self.password = self.config.get(self.Mail,"MailPassword").strip()
        except Exception as e:
            text = "Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,\
             e.__class__.__name__,\
             e.__class__,\
             e,\
             e.__class__.__doc__)
            print text


    def sendTextEmail(self,title,message,messagetype):
        '''
        发送文本邮件
        没有返回值
        函数内调用_format_addr()
        '''
        print 'sendTextEmail %s ' % title
        msg = MIMEText(message,'plain','utf-8')#中文参数‘utf-8’，单字节字符不需要
        msg[ 'From' ] = self._format_addr( u'%s<%s>' % ( self.mailName,self.sender ) )
        msg[ 'Subject' ] = Header( title )
        while True:
            try:

                #smtp = smtplib.SMTP( self.smtpserver , 25 , timeout = 30 )
                smtp = smtplib.SMTP()
                #smtp.set_debuglevel(1)
                print '开始尝试连接邮箱'
                smtp.connect(self.smtpserver,self.smtpserver_port)
                print '成功连接邮箱'
                print '开始尝试登陆邮箱'
                smtp.login( self.username , self.password )
                print '成功登陆邮箱'
                if (messagetype == "securityInfo"):
                    print '开始发送事件邮件'
                    msg[ 'To' ] = self._format_addr(u'Dollars<%s> ' % ','.join(self.receiver) )
                    # 这里有receiver为多个人时无法正确被格式化.
                    # ','join(self.receiver)无法正确格式化,貌似是%s长度有限制
                    # ''.join(self.receiver)只能格式化第一个邮箱地址
                    smtp.sendmail( self.sender , self.receiver , msg.as_string() )
                    print '成功发送事件邮件'
                else:
                    print '开始发送问题邮件'
                    msg[ 'To' ] = self._format_addr(u'Admin<%s>' % ','.join(self.receiver_admin) )
                    smtp.sendmail( self.sender , self.receiver_admin , msg.as_string() )
                    print '成功发送问题邮件'
            except  smtplib.SMTPAuthenticationError:
                print '认证失败,邮箱连接可能出问题了'
                self.count += 1
                if (self.count<3):
                    time.sleep(10)
                    continue
                else:
                    print '正在尝试更换邮箱...'
                    self.Mailchoose = not self.Mailchoose
                    self.mailInit(self.mailchoose)
                    #self.mailInit('backup')
                    self.count = 0
                    continue
            except Exception as e :
                text = "Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,\
                 e.__class__.__name__,\
                 e.__class__,\
                 e,\
                 e.__class__.__doc__)
                print text
                #time.sleep(5)
                continue
            else:
                smtp.quit()
                self.count = 0
                break


class mail(MailCreate):
    """docstring for mail"""
    def __init__(self, arg):
        super(mail, self).__init__(arg)




if __name__ == '__main__':

    test = MailCreate('测试机器人')
    #test.sendTextEmail("test",'good',"securityInfo")
    test.sendTextEmail("test",'good',"timereport")

    #test2 = mail('测试机器人')
    #while True:
        #test2.sendTextEmail("test",'test message',"securityInfo")
        #time.sleep(5)



