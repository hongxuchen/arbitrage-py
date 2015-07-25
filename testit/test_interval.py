#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sched
import sys
import time


# 每次调用的函数，打印round和执行的时间
def event(round):
    print ("Round {:02d}, time:{:20.4f}").format(round, time.time())

# 初始化scheduler
scheduler = sched.scheduler(time.time, time.sleep)
# 获得执行调度的初始时间
inittime = time.time()

# 总运行次数
total_round = 10
# 运行间隔
interval = 1
# 计数
update = 0

while update <= interval * total_round:
    # 设定调度 使用enterabs设定真实执行时间
    # 参数：1 执行时间（time.time格式）2 优先级 3 执行的函数 4 函数参数
    scheduler.enterabs(inittime + update, 1, event, (update + 1,))

    # 执行调度，会一直阻塞在这里，直到函数执行结束
    scheduler.run()

    # 输出屏幕
    sys.stdout.flush()

    # 增加计数值
    update = update + interval
