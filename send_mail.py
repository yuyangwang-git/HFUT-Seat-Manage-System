# -*- coding: utf8 -*-

import smtplib
from email.mime.text import MIMEText

class SendMail(object):
    
    def __init__(self):
        self.username = ''
        self.password = ''
        self.smtp_server = ''
        self.to_email = ''
        self.subjcet = ''
        self.message = ''

    def send(self):
        '''通过 SMTP 发送邮件'''
        msg = MIMEText(self.message, 'plain', 'utf-8')
        msg['From'] = self.username
        msg['To'] = 'Master<{}>'.format(self.to_email)
        msg['Subject'] = self.subject

        try:
            print('正在发送邮件...')
            server = smtplib.SMTP(self.smtp_server, 25)
            # server.set_debuglevel(1)
            server.login(self.username, self.password)
            server.sendmail(self.username, [self.to_email], msg.as_string())
            server.quit()
            print('邮件发送成功')
            return True
        except smtplib.SMTPException:
            print('邮件发送失败')
            return False

def main():
    e = SendMail()
    
    e.smtp_server = 'smtp.126.com'
    e.username = 'xxxxxxxx@126.com'
    e.password = 'xxxxxxxxxxxxxxxx'
    e.to_email = 'xxxxxx@gmail.com'
    
    e.subjcet = '这是一封测试邮件~'
    e.message = 'Lorem ipsum dolor sit amet, adipisicing elit'

    e.send()

if __name__  == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n操作已取消')
        exit(0)