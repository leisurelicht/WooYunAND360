# WooYunAND360
###用于同时对乌云,360补天和漏洞盒子上的新提交漏洞进行监视.

----
使用方法:


通过命令 python main.py 运行.等第一次运行结束后任务会加入后台运行.

因此请在第一遍运行中确保没有明显的报错.

因为使用了fork,所以目前只能在linux平台运行.

事件提醒通过邮件发送

----


程序基于python2.7

依赖包安装

* pip install -r requirements.txt


----

修改 Config/KeyWords.txt 文件可以增加要监看的关键字.格式为json.

基本格式为:

    {
        "%范围较大的第一个关键字%"KEY[1]:
        [
            {
                "KEY2":"%精确的第二个关键字%"KEY[2],
                "URL1":"%域名%"[URL]  
            }
        ]
    }
    
如果只有一个关键字可以只写域名
    
    {
        "%关键字%":
        [
            {
                "URL1":"%域名%"
            }
        ]
    }
    
没有域名也可以不写

     {
        "%关键字%":
        []
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
                KEY2":"宁夏",
                "URL":["bankofnx.com.cn","ycccb.com.cn"]
            }
        ],
        "同花顺":
        [
            {
                "URL1":"10jqka.com.cn"
            }
        ],
        "当当网":
        []
    
    }

关键字通过与标题和域名逐级比对确定是否为需要监看的事件.

规则为
    
    if KEY[1] in title:
        if KEY[2] and URL:
            if KEY[2]:
                if KEY[2] in title:
                    发送邮件
                elif KEY[2] in description:
                    发送邮件
            elif URL and 厂商域名:
                if URL == 厂商域名:
                    发送邮件
            else:
                检查下一个关键字
        else：
            发送邮件

不过目前只有wooyun可以用

----

配置 Config/mailconfig.ini 文件中的邮件设置.

[MailOne]为主要使用邮箱设置.

[MailTwo]为备用邮箱,主邮箱无法连接时会自动切换使用备用邮箱.

----

Events文件夹内保存已发送过通知邮件的事件

程序运行后会自动建立Events文件夹,无需手工创建

建立以后请不要删除,一直保存就好



