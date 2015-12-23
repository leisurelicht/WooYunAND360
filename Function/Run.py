#! usr/bin/env python
# -*- coding=utf-8 -*_
import time
import sched
import functools
from Site import fix360, WooYun, freebuf
from Common import mail
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


def robot_start_sign(arg):
    def sign(func):
        @functools.wraps(func)
        def deco():
            print '*'*100
            print('*'*18+arg+' 开始运行...! The time is: %s' % datetime.now()+'*'*10)
            print '*'*100
            time1 = datetime.now()
            func()
            print '*'*100
            print('*'*18+arg+' 运行结束! The time is: %s' % datetime.now()+'*'*10)
            print '*'*100
            print '*'*25, "本次运行共耗时,共耗时: ", (datetime.now()-time1), '*'*25
        return deco
    return sign


@robot_start_sign("机器人创建任务")
def init():
    global scheduled
    global robot_360
    global robot_WooYun
    global robot_FreeBuf
    global robot_time_report
    scheduled = sched.scheduler(time.time, time.sleep)
    robot_360 = fix360.fix360('../Config/KeyWords.txt', '../Events/EventsID360.txt')
    robot_WooYun = WooYun.WooYun('../Config/KeyWords.txt', '../Events/EventsID.txt')
    robot_FreeBuf = freebuf.FreeBuf('../Config/KeyWords.txt', '../Events/EventsIDFreeBuf.txt')
    robot_time_report = mail.MailCreate('运行报告')


@robot_start_sign("补天爬虫机器人")
def run_360():
    """
    调用fix360.py中的功能函数
    """
    robot_360.keyWordscheck(robot_360.dataAchieve(robot_360.dataRequest()))


@robot_start_sign("WooYun爬虫机器人")
def run_wooyun():
    """
    调用WooYun.py中的功能函数
    """
    robot_WooYun.keyWordscheck(robot_WooYun.dataAchieve(robot_WooYun.dataRequest()))


@robot_start_sign("漏洞盒子爬虫机器人")
def run_freebuf():
    """
    调用freebuf.py中的功能函数
    """
    robot_FreeBuf.keyWordscheck(robot_FreeBuf.dataAchieve(robot_FreeBuf.dataRequest()))


@robot_start_sign("启动报告机器人")
def run_time_start():
    """

    """
    robot_time_report.sendTextEmail('Start report', 'program start running', 'time_report')


@robot_start_sign("运行报告机器人")
def run_time_report():
    """

    """
    robot_time_report.sendTextEmail('Running report', 'program is running', 'time_report')


def run_robot():
    run_time_start()
    run_360()
    run_wooyun()
    run_freebuf()


def begin():
    init()
    run_robot()
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_360, 'interval', seconds=1800)
    scheduler.add_job(run_wooyun, 'interval', seconds=300)
    scheduler.add_job(run_freebuf, 'interval', seconds=3600)
    scheduler.add_job(run_time_report, 'interval', seconds=43200)
    scheduler.start()
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()  # Not strictly necessary if daemonic mode is enabled but should be done if possible


if __name__ == '__main__':
    begin()
