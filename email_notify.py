#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText

import time

sender = 'btc_hongxuchen@outlook.com'
receiver = 'leftcopy.chx@gmail.com'
server = 'localhost'

now = time.time()
raw_msg = 'now time: {:f}'.format(now)
msg = MIMEText(raw_msg)
msg['Subject'] = 'My Timer'
msg['From'] = sender
msg['To'] = receiver

session = smtplib.SMTP(server)
session.sendmail(sender, [receiver], msg.as_string())
session.quit()
