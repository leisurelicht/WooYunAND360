# WooYunAND360
###用于同时对乌云,360补天和漏洞盒子上的新提交漏洞进行监视.

----
使用方法:


通过命令 nohup python main.py & 就可以使程序进入后台运行.

简单的日志输出记录在nohup.out内

事件提醒通过邮件发送

----


程序基于python2.7

依赖包安装

* pip install -r requirements.txt


----

修改KeyWords.txt文件可以增加要监看的关键字.格式为json.

基本格式为:

    {
        "%范围较大的第一个关键字%":
        [
            {
                "KEY2":"%精确的第二个关键字%",
                "URL1":"%域名%"  #不过暂时还没用
            }
        ]
    }

范例如下:

    {
        "基金":
        [
            {
                "KEY2":"银华",
                "URL1":"yufund.com.cn"
            },
            {
                "KEY2":"嘉实",
                "URL1":"jsfund.cn"
            },
            {
                "KEY2":"长盛",
                "URL1":"csfunds.com.cn"
            }
        ],
        "银行":[
            {
                "KEY2":"宁夏",
                "URL1":"bankofnx.com.cn",
                "URL2":"ycccb.com.cn"
            }
        ]
    
    }

关键字通过与标题逐级比对确定是否为需要监看的事件.

----

配置mailconfig.ini文件中的邮件设置.

[MailOne]为主要使用邮箱设置.

[MailTwo]为备用邮箱,主邮箱无法连接时会自动切换使用备用邮箱.

----

Events文件夹内保存已发送过通知邮件的事件

程序运行后会自动建立Events文件夹,无需手工创建

建立以后请不要删除,一直保存就好



