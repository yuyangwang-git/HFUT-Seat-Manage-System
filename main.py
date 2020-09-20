# -*- coding: utf8 -*-

import requests
from hfut_vpn import HFUTVpn
from seat_manage_system import SeatManageSystem


class Student(object):
    '''用户信息'''
    
    def __init__(self, username, password, **kwargs):
        '''一些基本的用户信息
        
        Args:
            username: 学号
            password: 教务系统密码

            to_email:    可选，收件人邮箱地址
            from_email:  可选，寄件人邮箱地址 (需开通 SMTP 服务)
            from_pw:     可选，寄件人密码 (或授权码)
            smtp_server: 可选，SMTP 服务器地址
        '''
        self.username = username
        self.password = password

        if 'to_email' in kwargs:
            self.to_email = kwargs['to_email']
        if 'from_email' in kwargs:
            self.from_email = kwargs['from_email']
        if 'from_pw' in kwargs:
            self.from_pw = kwargs['from_pw']
        if 'smtp_server' in kwargs:
            self.smtp_server = kwargs['smtp_server']

def main():
    s = requests.session()
    student = Student('2017123123', 'xxxxxxx')
    
    # 可选信息
    student.to_email = 'xxxxxxxx@gmail.com'
    student.from_email = 'xxxxxx@126.com'
    student.from_pw = 'xxxxxxxxxxxxxxxxx'
    student.smtp_server = 'smtp.126.com'

    # 登录合肥工业大学 VPN
    vpn = HFUTVpn(s, student)
    vpn.login()

    # 登录图书馆座位管理系统
    seat = SeatManageSystem(s, student)
    seat.login()
    seat.getUserChoice()

    # 预约指定座位
    if seat.bookSpecificSeat():
       seat.sendBookInfo()

    # 随机预约可用座位
    # if seat.bookAvailableSeat(64, 5):
    #     seat.sendBookInfo()

    seat.logout()

if __name__  == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n操作已取消')
        exit(0)
