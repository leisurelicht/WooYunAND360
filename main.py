#! usr/bin/env python
# -*- coding=utf-8 -*-
import time
import sched
import fix360
import WooYun
from Common import mail
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

scheduled = sched.scheduler( time.time , time.sleep )
robot_360 = fix360.fix360('KeyWords.txt' , './Events/EventsID360.txt')
robot_WooYun = WooYun.WooYun('KeyWords.txt' , './Events/EventsID.txt')
robot_timereport = mail.MailCreate('运行报告')

def run360():
    print('*'*15+'360 start Running! The time is: %s' % datetime.now())
    robot_360.keyWordscheck(robot_360.dataAchieve(robot_360.dataRequest()))
    print('*'*15+'360 Running over! The time is: %s' % datetime.now())

def runWooYun():
    print('*'*15+'WooYun start Running! The time is: %s' % datetime.now())
    robot_WooYun.keyWordscheck(robot_WooYun.dataAchieve(robot_WooYun.dataRequest()))
    print('*'*15+'WooYun Running over! The time is: %s' % datetime.now())

def runtimeStart():
    print('*'*15+'Program Start Report! The time is: %s'% datetime.now())
    robot_timereport.sendTextEmail('Start report','program start running','timereport')
    print('*'*15+'Program Start Report over! The time is: %s' % datetime.now())

def runtimeReport():
    print('*'*15+'Time Report! The time is: %s' % datetime.now())
    robot_timereport.sendTextEmail('Running report','program is running','timereport')
    print('*'*15+'Time Report over! The time is: %s' % datetime.now())

def Start():
    runtimeStart()
    run360()
    runWooYun()

if __name__ == '__main__':
    runtimeStart()
    scheduler = BackgroundScheduler()
    scheduler.add_job(run360,'interval', seconds=1800)
    scheduler.add_job(runWooYun,'interval', seconds=60)
    scheduler.add_job(runtimeReport,'interval', seconds=43200)
    scheduler.start()
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()  # Not strictly necessary if daemonic mode is enabled but should be done if possible

