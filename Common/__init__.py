# /user/bin/env python
#-*-coding=utf-8-*-

import common
import database
import decorators
import filehandle
import mail

print "******模块功能检查开始******"

print "******开始检查邮箱配置及功******」"
test = mail.MailCreate('测试机器人')
a,b = test.get_mail_config
print a,b


print "******邮箱配置及功能检查结束******"