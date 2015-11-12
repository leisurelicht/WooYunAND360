# WooYunAND360
###用于同时对乌云,360补天和漏洞盒子上的新提交漏洞进行监视.

----
使用方法:


通过命令 nohup python main.py & 就可以使程序进入后台运行.

简单的日志输出记录在nohup.out内

事件提醒通过邮件发送

----


程序基于python2.7

依赖的第三方包有:

BeautifulSoup4.3.2

requests2.5.3

apscheduler3.0.3

对漏洞盒子的监控需要支持ssl连接.

----

修改KeyWords.txt文件可以增加要监看的关键字.每个关键字后换行保存即可.

关键字通过与标题比对确定是否为需要监看的事件.

----

配置mailconfig.ini文件中的邮件设置.

[MailOne]为主要使用邮箱设置.

[MailTwo]为备用邮箱,主邮箱无法连接时会自动切换使用备用邮箱.

