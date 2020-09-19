# 合肥工业大学图书馆座位预约程序

合工大 WebVPN (vpn.hfut.edu.cn) 登录及屯溪路校区图书馆座位预约程序，可预约指定座位或任意一个可用座位

```
├─ .git
├─ LICENSE
├─ README.md
├─ hfut_vpn.py                         # WebVPN 登录模块
├─ main.py                             # 主程序
├─ seat_manage_system.py               # 座位管理系统登录及预约模块
└─ send_mail.py                        # SMTP 邮件发送模块
```

## Usage

修改 main.py 中的学号、密码和希望用于接收预约结果的邮件地址（可选）

如果需要预约指定座位，调用`bookSpecificSeat()`方法

如果希望预约任意一个可用座位，调用`bookAvailableSeat(times, secs)`方法

```bash
$ py main.py
```

然后按提示选择预约区域及日期即可
