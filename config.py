import os

ENSURE_LOGIN_MINUTE = '*/15'
ENSURE_LOGIN_HOUR = '*' 

# 汇报时间，使用crontab格式，用逗号分隔多个时间
REPORT_MINUTE = '10'
REPORT_HOUR = '8'

REPORT_MAX_ERROR_RETRY_COUNT = 60

# 用户名
USERNAME = ""
# 密码
PASSWORD = ""
# 是否在校 0=否，杨凌； 1=是； ty=否，太原
IS_ATSCHOOL = "1"

SESSION = ""
USERAGENT = "Mozilla/5.0 (Linux; Android 12; XIAOMI Build/QKQ1.220910.003; wv) AppleWebKit/538.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.3865.120 MQQBrowser/6.3 TBS/045438 Mobile Safari/537.36 wxwork/3.1.0 MicroMessenger/7.2.1 NetType/WIFI Language/zh Lang/zh"

# ServerChan的推送链接
PUSH = ""

# 邮件推送. 
# 收件人
MAIL_RECEIVER = "" 
# 发件配置
MAIL_SMTP_HOST = ""
MAIL_SMTP_PORT = 587
MAIL_SMTP_SECURITY = "" # none / ssl / tls
MAIL_SMTP_USERNAME = ""
MAIL_SMTP_PASSWORD = ""
MAIL_FROM = ""
