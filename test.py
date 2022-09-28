from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
import logging

def test_print():
    logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ok")
    raise Exception("test")

scheduler = BlockingScheduler()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("run")
    scheduler.add_job(test_print, trigger="cron", hour='*', minute='*/1', timezone="Asia/Shanghai")
    scheduler.start()