import os

import schedule
import time
from datetime import datetime, timedelta

from bot import x
from bot.story import Story
from job.get import NUA, tokyo_timestamp

from dotenv import load_dotenv

load_dotenv()


def send():
    story = Story()
    tweets_subjects, tweets_others = story.now_class()

    # 测试推送
    bot = x.Bot()

    # 认证 Twitter API
    api = bot.authenticate_twitter()

    # 发送连发推文
    bot.send_tweets(api, tweets_subjects + tweets_others)


def check_today_in_dates(filepath):
    # 读取日期文件
    with open(filepath, encoding="utf-8-sig") as file:
        dates = file.readlines()

    # 去除换行符并转换为日期对象，只考虑月日，忽略年份
    dates = [datetime.strptime(date.strip(), "%m月%d日").date().replace(year=1) for date in dates]

    # 获取东京时间戳
    tokyo_ts = tokyo_timestamp()
    tokyo_time = datetime.fromtimestamp(tokyo_ts)
    today = tokyo_time.date().replace(year=1)

    # 如果今天是周日（东京时间），返回 False
    if tokyo_time.weekday() == 6:  # 周日对应的 weekday() 值为 6
        return False

    # 检查今天的月日是否在日期列表中
    return today in dates


def run():
    if check_today_in_dates("teaching_dates.csv"):
        send()
        return True
    else:
        print("Today is not a teaching day, sleeping for 24 hours.")
        return False


if __name__ == '__main__':
    run()
