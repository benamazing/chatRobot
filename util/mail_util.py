# -*- coding:utf-8 -*-
# encoding=utf-8

import logging
from email.mime.text import MIMEText
import json
import smtplib
from email.header import Header
from email import encoders

logging.basicConfig(level=logging.ERROR)


class MailService(object):

    def __init__(self, smtp_server, from_addr, password):
        self.smtp_server = smtp_server
        self.from_addr = from_addr
        self.password = password

    def send_html_mail(self, to_addr, subject=None, html_text=None):
        msg = MIMEText(html_text, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8').encode()
        try:
            server = smtplib.SMTP(self.smtp_server, 25, timeout=10)
            server.login(self.from_addr, self.password)
            server.sendmail(self.from_addr, to_addr, msg.as_string())
            server.quit()
        except:
            logging.exception('Failed to send html format mail: ')

    def send_text_mail(self, to_addr, subject=None, plain_text=None):
        msg = MIMEText(plain_text, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8').encode()
        try:
            server = smtplib.SMTP(self.smtp_server, 25, timeout=10)
            server.login(self.from_addr, self.password)
            server.sendmail(self.from_addr, to_addr, msg.as_string())
            server.quit()
        except:
            logging.exception('Failed to send plain text mail.')


with open("../conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    smtp_server = conf['smtp_server']
    from_addr = conf['smtp_from']
    password = conf['smtp_password']

mail_service = MailService(smtp_server, from_addr, password)
