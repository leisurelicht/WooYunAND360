# WooYunAND360
###用于同时对乌云,360补天和漏洞盒子上的新提交漏洞进行监视.

----
使用方法:


通过命令 python main.py 运行.等第一次运行结束后任务会加入后台运行.

因此请在第一遍运行中确保没有明显的报错.

因为使用了fork,所以目前只能在linux平台运行.

事件提醒通过邮件发送

    2016/5/25
    增加不同漏洞向不同地址发送邮件的功能

    

----


程序基于python2.7

依赖包安装

* pip install -r requirements.txt


----

修改 Config/KeyWords.txt 文件可以增加要监看的关键字,格式为json.

基本格式为:

    {
        "%范围较大的第一个关键字%"KEY[1]:
        [
            {
                "KEY2":"%精确的第二个关键字%"KEY[2],
                "URL1":"%域名%"[URL]
                "TAG":1
            }
        ]
    }
    
如果只有一个关键字可以只写域名
    
    {
        "%关键字%":
        [
            {
                "URL1":"%域名%"
                "TAG":1
            }
        ]
    }
    
没有域名也可以不写

     {
        "%关键字%":
        [
            "TAG":1
        ]
    }

只有TAG不可省略,TAG为一个正整数

范例如下:

    {
        "基金":
        [
            {
                "KEY2":"银华",
                "URL":"yufund.com.cn",
                "TAG":1
            },
            {
                "KEY2":"嘉实",
                "URL":"jsfund.cn",
                "TAG":2
            },
            {
                "KEY2":"长盛",
                "URL":"csfunds.com.cn",
                "TAG":3
            },
            {
                "KEY2":"诺安",
                "TAG":4
            }
        ],
        "银行":
        [
            {
                "KEY2":"宁夏",
                "URL":["bankofnx.com.cn","ycccb.com.cn"],
                "TAG":5
            }
        ],
        "新浪":
        [
            {
                "URL":"sina.com.cn",
                "TAG":6
            }
        ],
        "联通":
        [
            {
                "KEY2":"中国",
                "TAG":6
            }
        ],
        "华为":
        [
            {
                "TAG":7
            }
        ]
    }

关键字通过与标题和域名逐级比对确定是否为需要监看的事件.

只有wooyun和360补天可以用

----

配置 Config/mailconfig.ini 文件中的邮件设置.

[MailOne]为主要使用邮箱设置.

[MailTwo]为备用邮箱,主邮箱无法连接时会自动切换使用备用邮箱.

配置 Config/mail_address.ini 文件增加用户邮箱地址

    Admin_Address:ReceiveMail_Admin的value为邮箱地址,接受运行报告邮件和异常邮件
    User_Address下的key为邮箱地址,接收安全事件邮件
    value为KeyWords中的TAG,不同的漏洞事件向相应的地址发送邮件,'*'代表全选所有TAG
    
范例为:

    [Admin_Address]
    ReceiverMail_Admin : xxx@126.com,yyy@163.com,zzz@qq.com
    [User_Address]
    xxx@126.com:1,3,5,6,7 //当出现TAG为1、3、5、6、7的事件时向xxx@126邮箱发邮件
    yyy@163.com:2,4,5,7
    zzz@qq.com:5
    aaa@gmail.com:* //所有事件都向aaa.@gmail.com邮箱发邮件

----

Events文件夹内保存已发送过通知邮件的事件

程序运行后会自动建立Events文件夹,无需手工创建

建立以后请不要删除,一直保存就好



