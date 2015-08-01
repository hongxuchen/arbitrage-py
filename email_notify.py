#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText

import common


def send_msg(report):
    emailing_info = common.get_key_from_data('Emailing')
    sender = emailing_info['sender']
    receiver = emailing_info['receiver']
    server = emailing_info['server']
    msg = MIMEText(report)
    msg['Subject'] = 'Asset Report'
    msg['From'] = sender
    msg['To'] = receiver
    session = smtplib.SMTP(server)
    session.sendmail(sender, [receiver], msg.as_string())
    session.quit()


import sched, time
from threading import Thread, Timer

s = sched.scheduler(time.time, time.sleep)


class Job(Thread):
    def run(self):
        print_time()
        print('working')


def each_day_time(hour, min, sec, next_day=True):
    struct = time.localtime()
    if next_day:
        day = struct.tm_mday + 1
    else:
        day = struct.tm_mday
    return time.mktime((struct.tm_year, struct.tm_mon, day,
                        hour, min, sec, struct.tm_wday, struct.tm_yday,
                        struct.tm_isdst))


def print_time(name="None"):
    print(time.ctime())


def do_somthing():
    job = Job()
    job.start()


def echo_start_msg():
    print('starting')


def main():
    s.enterabs(each_day_time(1, 0, 0, True), 1, echo_start_msg, ())
    s.run()
    while (True):
        Timer(0, do_somthing, ()).start()


if __name__ == '__main__':
    print(each_day_time(1, 0, 0, True))
    # main()
    # print_time()
