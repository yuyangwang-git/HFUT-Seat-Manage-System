# -*- coding: utf8 -*-

import requests
import time
import random
from retry import retry
from send_mail import SendMail

class SeatManageSystem(object):
    '''座位管理系统登录、座位预约等操作'''

    def __init__(self, session, student):
        self.session = session
        self.stu = student

        # 用户选择的区域和日期
        self.user_choice = {
            'area' : 16,
            'day' : ''
        }

        # 登录返回的数据
        # 学校甚至能把身份证号QQ微信邮箱全发送给用户
        # 和新教务系统返回任课老师学号等个人信息有异曲同工之妙hhh
        # <del> 隐私不值钱.jpg </del>
        self.login_response = {}

        # 获取可预约日期时返回的数据
        self.space_day = {}

        # 获取可预约时间段时返回的数据
        self.space_time_bucket = {}

        # 获取当前座位信息时返回的数据（我也不知道学校为什么这么给变量命名）
        self.space_old = {}

        # 预约时返回的结果
        self.book_result = {}

        # 所选区域座位计数
        self.seat_count = {
            'empty' : 0,
            'full' : 0,
            'all' : 0
        }

        # 所选区域空闲座位 name-id dict
        self.empty_seat = {}

        # 座位管理系统主页前缀
        self.base_url = 'https://vpn.hfut.edu.cn/http/77726476706e69737468656265737421a2a611d2736526022a5ac7f4ca/'

        self.captcha_url = self.base_url + 'api.php/check'                                         # 验证码
        self.login_url = self.base_url + 'api.php/login'                                           # 登录
        self.logout_url = self.base_url + 'api.php/logout'                                         # 退出
        self.space_day_url = self.base_url + 'api.php/space_days/{}'                               # 预约可用天
        self.space_time_bucket_url = self.base_url + 'api.php/space_time_buckets'                  # 预约可用时间段
        self.seat_info_url = self.base_url + 'api.php/spaces_old'                                  # 座位使用情况
        self.book_url = self.base_url + 'api.php/spaces/{}/book'                                   # 预定
        # self.status_url = self.base_url + 'api.php/profile/books/{}'                               # 

        # ?vpn-12-o1-210.45.242.82                                                                 # 调试时发现的可有可无的参数
    
    def __getCaptcha(self):
        '''验证码的获取和保存'''
        captcha = self.session.get(self.captcha_url)
        with open('captcha.png', 'wb') as f:
            f.write(captcha.content)
        
        verify = input('请输入验证码：')
        return str(verify)
    
    @retry(tries=3)                                                                                # 应该是校园网问题，经常出现返回的数据不正确，故出现异常时尝试三次
    def login(self):
        '''登录座位管理系统'''
        login_form_data = {
            'username': self.stu.username,
            'password': self.stu.password,
            'verify': self.__getCaptcha()
        }

        self.login_response = self.session.post(self.login_url, data=login_form_data).json()       # 尝试登录座位管理系统

        if int(self.login_response['status']) == 0:
            print('座位管理系统登录失败，请重试')
        else:
            name = self.login_response['data']['list']['name']
            print(f'座位管理系统登录成功，欢迎{name}~')
    
    @retry(tries=3)
    def logout(self):
        '''退出座位管理系统，实际上只要两分钟没有任何操作系统就会自行退出'''
        logout_form_data = {
            'access_token': self.login_response['data']['_hash_']['access_token'],
            'userid': self.stu.username,
        }

        self.logout_response = self.session.post(self.logout_url, data=logout_form_data).json()

        if int(self.logout_response['status']) == 1:
            print('退出成功')

    def getUserChoice(self):
        area_dict = {
            '0' : 5,         # 二楼书库 5
            '1' : 6,         # 二楼期刊阅览室 6
            '2' : 14,        # 三楼夹层 14
            '3' : 15,        # 三楼平层南区 15
            '4' : 16,        # 三楼平层北区 16
            '5' : 8,         # 四楼自习区 8
            '6' : 11,        # 四楼电子阅览室 11
            '7' : 13,        # 五楼书库 13
            '8' : 10         # 六楼书库 10
        }

        area = input('请选择你要预约的区域(留空则选择三楼平层北区): \n'
            '0 二楼书库\n'
            '1 二楼期刊阅览室\n'
            '2 三楼夹层\n'
            '3 三楼平层南区\n'
            '4 三楼平层北区\n'
            '5 四楼自习区\n'
            '6 四楼电子阅览室\n'
            '7 五楼书库\n'
            '8 六楼书库\n')

        if area == '':
            self.user_choice['area'] = area_dict['4']
        else:
            self.user_choice['area'] = area_dict[area]
        
        if input('预定今天的座位吗？（y/n）') == 'y':
            self.user_choice['day'] = 0
            print('即将预定今天的座位')
        else:
            self.user_choice['day'] = 1
            print('即将预定明天的座位')

    @retry(tries=3)
    def __getSpaceDay(self):
        '''获取预约可用天'''
        self.space_day = self.session.get(self.space_day_url.format(self.user_choice['area'])).json()
    
    @retry(tries=3)
    def __getSpaceTimeBucket(self):
        '''获取可用预约时间
        
        <del>辣鸡服务器甚至没有校验参数，实际上可以预约任意一天的座位www</del>
        '''
        if int(self.user_choice['day']) == 0:
            self.user_choice['day'] = self.space_day['data']['list'][0]['day']
        else:
            self.user_choice['day'] = self.space_day['data']['list'][1]['day']

        space_time_param = {
            'day' : self.user_choice['day'],
            'area' : self.user_choice['area']
        }

        self.space_time_bucket = self.session.post(self.space_time_bucket_url,\
            data=space_time_param).json()                                                          # 获取可预约时间

    @retry(tries=3)
    def __getSeatInfo(self):
        '''获取所有座位信息'''
        time_param = {
            'area' : self.user_choice['area'],
            'segment' : self.space_time_bucket['data']['list'][0]['bookTimeId'],
            'day' : self.user_choice['day'],
            'startTime' : self.space_time_bucket['data']['list'][0]['startTime'],
            'endTime' : self.space_time_bucket['data']['list'][0]['endTime']
        }                                                                                          # 构造 parameters

        self.space_old = self.session.get(self.seat_info_url, params=time_param).json()            # 获取座位信息
        seat_info = self.space_old['data']['list']

        count = 0                                                                                  # 统计空余座位
        for i in range(len(seat_info)):
            if int(seat_info[i]['status']) == 1:
                self.empty_seat[seat_info[i]['name']] = seat_info[i]['id']
                print(seat_info[i]['name'])                                                        # 列出所有空闲座位号
                count = count + 1
        
        all_seats = len(seat_info)
        self.seat_count['all'] = all_seats
        self.seat_count['empty'] = count
        self.seat_count['full'] = all_seats - count

        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())                           # 格式化成 2020-09-16 19:45:33 形式

        print(f'截至 {localtime} 该区域共有 {all_seats} 个座位，其中 {count} 个空闲')

    def __bookSeat(self, seat_id):
        '''提交座位预定请求

        Args:
            seat_id: 希望预约的座位 id (不是刷卡机器上的座位编号)

        Returns:
            预约成功时返回 True
        '''
        self.book_form_data = {
            'access_token': self.login_response['data']['_hash_']['access_token'],
            'userid': self.stu.username,
            'segment': self.space_time_bucket['data']['list'][0]['bookTimeId'],
            'type': 1                                                                              # 疑似使用此参数判断本科生身份
        }

        self.book_result = self.session.post(self.book_url.format(seat_id), \
            data=self.book_form_data).json()                                                       # 尝试预定座位

        if int(self.book_result['status']) == 1:
            seat_name = self.book_result['data']['list']['spaceInfo']['name']
            print(f'预约成功，您的座位号是 {seat_name}')
            return True
        else:
            print(self.book_result['msg'])
            return False

    def bookSpecificSeat(self):
        '''预约指定座位，建议在预约次日座位时使用
        
        Returns:
            预约成功时返回 True
        '''
        self.__getSpaceDay()
        self.__getSpaceTimeBucket()
        self.__getSeatInfo()

        seat_name = input('希望预定的座位号：')
        if int(seat_name) > int(self.seat_count['all']):
            print('未找到该座位，请检查输入')
        elif not seat_name in self.empty_seat:
            print('该座位已被占用，请尝试其它座位')
        else:
            return self.__bookSeat(self.empty_seat[seat_name])
        
        return False

    def bookAvailableSeat(self, times, secs):
        '''预约任意一个可用座位，建议在预约当日座位时调用
        
        Args:
            times: 尝试预约次数
            secs: 每次尝试的时间间隔

        Returns:
            预约成功时返回 True
        '''
        self.__getSpaceDay()
        self.__getSpaceTimeBucket()
        self.__getSeatInfo()

        if len(self.empty_seat.keys()) != 0:                                                       # 存在空闲座位
            seat_id = random.choice(list(self.empty_seat.values()))                                # 随机选择一个空闲座位
            return self.__bookSeat(seat_id)
        else:
            for i in range(times):
                self.__getSpaceTimeBucket()
                self.__getSeatInfo()

                if len(self.empty_seat.keys()) != 0:
                    seat_id = random.choice(list(self.empty_seat.values()))
                    return self.__bookSeat(seat_id)
                
                time.sleep(secs)
            
            print(f'已尝试预约 {times} 次，均失败')
            return False

    def sendBookInfo(self):
        '''将预约成功信息发送到邮箱'''
        seat_name = self.book_result['data']['list']['spaceInfo']['name']
        book_time = self.book_result['data']['list']['beginTime']['date']
        deadline = time.mktime(time.strptime(book_time, '%Y-%m-%d %H:%M:%S')) + 1800
        deadline = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(deadline))                    # 格式化成 2020-09-16 19:45:33 形式

        mail = SendMail()
        mail.smtp_server = self.stu.smtp_server
        mail.username = self.stu.from_email
        mail.password = self.stu.from_pw
        mail.to_email = self.stu.to_email
        mail.subject = f'已成功预约 {seat_name} 号座位'
        mail.message = (f'已成功为您预约了位于三楼平层北区的 {seat_name} 号座位~\n\n'
            f'预约开始时间: {book_time}\n'
            f'请务必于 {deadline} 之前抵达图书馆并签到\n\n'
            '“While there\'s life, there\'s hope.”\n'
            '    ― Marcus Tullius Cicero\n')
        
        mail.send()

"""     暂时没有找到获取已预约记录id的比较简单的方法，以后再添加 
        # self.status_form_data = {
        #     '_method': 'delete',
        #     'id': '',
        #     'userid': student.username,
        #     'access_token': ''
        # }   
        @retry(tries=3)
        def deleteSeat(self):
            '''取消已预定的座位'''
            self.status_form_data['access_token'] = self.login_response['data']['_hash_']['access_token']

            self.status_url = self.status_url.format(book_id)
            self.status_form_data['_method'] = 'delete'
            result = self.session.get(self.status_url, data=self.status_form_data).json()

            if int(result['status']) == 0:
                print('没有登录或登录超时，请重试')
            else:
                print('预约取消成功') """

def main():
    pass

if __name__  == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n操作已被用户取消')
        exit(0)