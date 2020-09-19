# -*- coding: utf8 -*-

import requests

class HFUTVpn(object):
    '''合肥工业大学VPN (vpn.hfut.edu.cn) 登录相关操作'''

    def __init__(self, session, student):
        self.session = session
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/85.0.4183.102 Safari/537.36',
            'Connection': 'keep-alive'
        }                                                                                          # 经测试不添加 header 仍可正常访问
        self.form_data = {
            'auth_type': 'local',
            'username': student.username,
            'sms_code': '',
            'password': student.password,
            'captcha': '',
            'needCaptcha': 'false',
            'captcha_id': '',
        }                                                                                          # 貌似只要 post false 就永远不需要验证码hhh
        self.do_login_url = 'https://vpn.hfut.edu.cn/do-login'                                     # 登录 URL

    def login(self):
        r = self.session.post(self.do_login_url, data=self.form_data, headers=self.header).json()

        if r['success'] == True:
            print("合肥工业大学VPN登录成功")
        else:
            print("VPN登录失败，请检查学号和密码")

def main():
    Student = type('Student', (object,), dict())
    
    student = Student()
    student.username = 'xxxxxxx'
    student.password = 'xxxxxxx'
    
    s = requests.session()

    vpn = HFUTVpn(s, student)
    vpn.login()

if __name__  == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n操作已取消')
        exit(0)