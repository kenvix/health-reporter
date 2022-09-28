import datetime
import os
import re
import config
import requests
import logging
import json
import random
import sys
import time
import threading
import sign_locations
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR

if config.SESSION is None or len(config.SESSION) == 0:
    config.SESSION = os.getenv("eai-sess")

if config.USERNAME is None or len(config.USERNAME) == 0:
    config.USERNAME = os.getenv("USERNAME")

if config.PASSWORD is None or len(config.PASSWORD) == 0:
    config.PASSWORD = os.getenv("PASSWORD")

if config.IS_ATSCHOOL is None or len(config.IS_ATSCHOOL) == 0:
    config.IS_ATSCHOOL = os.getenv("IS_ATSCHOOL")

session = requests.Session()
session.cookies["eai-sess"] = config.SESSION
session.headers["User-agent"] = config.USERAGENT
session.headers["Referer"] = "https://app.nwafu.edu.cn/ncov/wap/default/index"
session.headers["Accept-language"] = "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
# session.headers["dnt"] = "1"
# session.headers["sec-ch-ua"] = '"Chromium";v="104", " Not A;Brand";v="99", "Microsoft Edge";v="104"'
# session.headers["sec-ch-ua-mobile"] = "?1"
# session.headers["sec-ch-ua-platform"] = '"Android"'
# session.headers["sec-fetch-dest"] = "document"
# session.headers["sec-fetch-mode"] = "navigate"
# session.headers["sec-fetch-site"] = "none"
# session.headers["sec-fetch-user"] = "?1"
# session.headers["upgrade-insecure-requests"] = "1"

errs = 0
reportErrorCount = 0
scheduler = BlockingScheduler()

form_data = {
    "zgfxdq": "0",
    "mjry": "0",
    "csmjry": "0",
    "tw": "1",
    "sfcxtz": "0",
    "sfjcbh": "0",
    "sfcxzysx": "0",
    "qksm": "",
    "sfyyjc": "0",
    "jcjgqr": "0",
    "remark": "",
    "address": None,
    "geo_api_info": None,
    "area": "陕西省 咸阳市 杨陵区",
    "province": "陕西省",
    "city": "咸阳市",
    "sfzx": config.IS_ATSCHOOL,
    "sfjcwhry": "0",
    "sfjchbry": "0",
    "sfcyglq": "0",
    "gllx": "",
    "glksrq": "",
    "jcbhlx": "",
    "jcbhrq": "",
    "ismoved": "0",
    "bztcyy": "",
    "sftjhb": "0",
    "sftjwh": "0",
    "jcjg": "",
    "fxyy": "　"
}


def update_form_data():
    if config.IS_ATSCHOOL == "1":
        geo_api_info = sign_locations.geo_api_info_in_school[
            random.randint(0, len(sign_locations.geo_api_info_in_school) - 1)
        ]
    elif config.IS_ATSCHOOL == "0":
        geo_api_info = sign_locations.geo_api_info_not_in_school[
            random.randint(
                0, len(sign_locations.geo_api_info_not_in_school) - 1)
        ]
    elif config.IS_ATSCHOOL == "ty":
        geo_api_info = sign_locations.geo_api_info_in_taiyuan[
            random.randint(0, len(sign_locations.geo_api_info_in_taiyuan) - 1)
        ]
    else:
        raise Exception(
            "Invalid IS_ATSCHOOL value: {}".format(config.IS_ATSCHOOL))

    form_data["area"] = "%s %s %s" % (geo_api_info["addressComponent"]["province"],
                                      geo_api_info["addressComponent"]["city"],
                                      geo_api_info["addressComponent"]["district"]
                                      )
    form_data["province"] = geo_api_info["addressComponent"]["province"]
    form_data["city"] = geo_api_info["addressComponent"]["city"]
    form_data["address"] = geo_api_info["formattedAddress"]
    form_data["geo_api_info"] = json.dumps(geo_api_info, ensure_ascii=False)
    form_data["sfzx"] = "1" if config.IS_ATSCHOOL == "1" else "0"
    return


msglogger = logging.getLogger("msg")


class SignException(Exception):
    def __init__(self, msg, code=-1):
        self.msg = msg
        self.code = code
    
    def __str__(self):
        return str(self.code) + " - " + self.msg


def confirm_login():
    global errs1
    data = session.get(
        "https://app.nwafu.edu.cn/ncov/wap/default/index", allow_redirects=False)
    if data.status_code == 200:
        errs = 0
        return True
    else:
        raise SignException("Login session expired.")


def do_login():
    form_data = {
        "username": config.USERNAME,
        "password": config.PASSWORD
    }
    submit_data = {}
    submit_data.update(form_data)
    data = session.post(
        "https://app.nwafu.edu.cn/uc/wap/login/check", data=submit_data)
    rsp = ""
    if data.status_code >= 200 and data.status_code < 400:
        try:
            rsp = data.json()
            if rsp["e"] != 0:
                raise SignException(rsp["m"], rsp["e"])
            # cookies saved by py requests
        except Exception as e:
            raise SignException("JSON decode failed: " +
                                rsp + "; Exception: " + str(e))
    else:
        raise SignException(
            "Login Operation Failed. (SERVER ERROR CODE: {})".format(data.status_code), data.status_code)


def do_login_loop():
    global errs
    while True:
        try:
            do_login()
            break
        except Exception as e:
            msglogger.warning(e)
            msglogger.warning("Login failed, retry after 10 seconds.")
            time.sleep(10)


def confirm_login_loop():
    global errs
    while True:
        try:
            confirm_login()
            break
        except Exception as e:
            msglogger.warning(e)
            msglogger.warning("Login expired, login after 10 seconds.")
            time.sleep(10)
            do_login_loop()


def report():
    global errs
    form_data["tw"] = str(random.randrange(1, 2))
    update_form_data()
    submit_data = {}
    submit_data.update(form_data)

    data = session.post(
        "https://app.nwafu.edu.cn/ncov/wap/default/save", data=submit_data)
    rsp = ""
    try:
        rsp = data.json()
    except Exception as e:
        raise SignException("JSON decode failed: " +
                            rsp + "; Exception: " + str(e))

    if rsp["e"] != 0:
        raise SignException(rsp["m"], rsp["e"])

    send_msg("西农健康打卡成功，位于 " + form_data["address"], "Time: %s\r\nServer Response: \r\n%s\r\n\r\nClient Request: \r\n%s" % (
        str(datetime.datetime.now()),
        json.dumps(rsp, indent=4, sort_keys=True, ensure_ascii=False),
        json.dumps(submit_data, indent=4, sort_keys=True, ensure_ascii=False)
    ))
    errs = 0


def report_loop():
    global reportErrorCount
    lastError = ""
    while reportErrorCount <= config.REPORT_MAX_ERROR_RETRY_COUNT:
        try:
            report()
            reportErrorCount = 0
            msglogger.info("Successfully reported!")
            return
        except Exception as e:
            msglogger.error("Report failed.")
            msglogger.error(e)
            reportErrorCount += 1
            lastError = str(e)
            time.sleep(60)
    
    if reportErrorCount > config.REPORT_MAX_ERROR_RETRY_COUNT:
        msglogger.error("Report failed too many times, exiting.")
        send_msg("西农健康打卡失败！！！位于 " + form_data["address"], "Time: %s\r\nServer Exception: \r\n%s\r\n\r\nClient Request: \r\n%s" % (
            str(datetime.datetime.now()),
            lastError,
            json.dumps(form_data, indent=4, sort_keys=True, ensure_ascii=False)
        ))
        reportErrorCount = 0


def send_msg(title, content = ""):
    msglogger.info(content)
    if config.MAIL_RECEIVER is not None and len(config.MAIL_RECEIVER) >= 1 and config.MAIL_SMTP_HOST is not None and len(config.MAIL_SMTP_HOST) >= 1 and config.MAIL_SMTP_PORT is not None and config.MAIL_SMTP_USERNAME is not None and len(config.MAIL_SMTP_USERNAME) >= 1 and config.MAIL_SMTP_PASSWORD is not None and len(config.MAIL_SMTP_PASSWORD) >= 1:
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = config.MAIL_FROM
        msg['To'] = config.MAIL_RECEIVER
        msg['Subject'] = Header(title, 'utf-8')
        try:
            if config.MAIL_SMTP_SECURITY == "none" or config.MAIL_SMTP_SECURITY == "tls":
                smtp = smtplib.SMTP(config.MAIL_SMTP_HOST, config.MAIL_SMTP_PORT)
            elif config.MAIL_SMTP_SECURITY == "ssl":
                smtp = smtplib.SMTP_SSL(config.MAIL_SMTP_HOST, config.MAIL_SMTP_PORT)

            smtp.login(config.MAIL_SMTP_USERNAME, config.MAIL_SMTP_PASSWORD)
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())
            smtp.quit()
            msglogger.info("Successfully sent email.")
        except Exception as e:
            msglogger.error("Failed to send email.")
            msglogger.error(e)

    if config.PUSH is not None and len(config.PUSH) >= 1:
        requests.post(config.PUSH, data={"text": title, "desp": content})


# def event_handle(event):
#     global errs
#     if event.exception:
#         errs += 1
#         if errs > 3:
#             send_msg(str(event.exception))
#             if isinstance(event.exception, SignException):
#                 scheduler.remove_all_jobs()
#                 threading.Thread(target=lambda: scheduler.shutdown()).start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    update_form_data()
    do_login()
    if '-f' not in sys.argv:
        msglogger.info("Ensuring login")
        if config.SESSION is None or len(config.SESSION) == 0:
            do_login_loop()
        confirm_login_loop()
        msglogger.info("Ensured login")

    if '-s' in sys.argv:
        msglogger.info("FORCE sign command exist. sign now")
        report()

    scheduler.add_job(confirm_login_loop, trigger="cron", hour=config.ENSURE_LOGIN_HOUR,
                      minute=config.ENSURE_LOGIN_MINUTE, timezone="Asia/Shanghai")
    scheduler.add_job(report_loop, trigger="cron", hour=config.REPORT_HOUR,
                      minute=config.REPORT_MINUTE, timezone="Asia/Shanghai")
    scheduler.start()
