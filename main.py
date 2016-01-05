#! usr/bin/env python
# -*- coding=utf-8 -*-
import os
from Function import Run

#
# pid = os.fork()
pid1 = os.fork()
# if pid == 0:
#     print "进程1启动成功 %s,%s" % (pid, os.getpid())
    # os.system("python ./WebSite/WebSite.py")
if pid1 == 0:
    print "进程2启动成功 %s,%s" % (pid1, os.getpid())
    os.chdir('./Function/')
    Run.begin()

print "所有进程启动结束"