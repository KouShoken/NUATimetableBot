import os

import schedule
import time
from datetime import datetime, timedelta, timezone

from bot.story import Story
from bot.x_apiv2 import Tweets
from job.get import NUA, tokyo_timestamp, TimeList

from dotenv import load_dotenv

load_dotenv()


def send():
    # 获取当前时间戳
    current_timestamp = tokyo_timestamp()
    current_date = datetime.fromtimestamp(current_timestamp, timezone(timedelta(hours=9)))

    # 获取当前的限数
    current_period = NUA().get_period(current_timestamp)

    # ! 0限不運行
    if current_period == 0:
        print("Not in a Period Time.")
        exit()

    # 格式化当前限数
    formatted_period = Story().now_format_period(current_period)

    # 从时间戳获取当前的星期几
    weekday_kanji = ['月', '火', '水', '木', '金', '土', '日']
    current_weekday = datetime.fromtimestamp(current_timestamp, timezone(timedelta(hours=9))).weekday()

    # 获取实时课程表数据
    timetable_data = TimeList().get_realtime_class(timestamp=current_timestamp)

    # 格式化课程表
    formatted_timetable = Story().now_format_timetable(timetable_data)

    tweet = (f"{current_date.strftime('%m/%d')}({weekday_kanji[current_weekday]}) "
             f"{formatted_period} "
             f"#日芸はこんな授業してる #春から日芸\n\n{formatted_timetable}")

    print(tweet)

    # SEND
    tweets = Tweets()
    tweets.auto_post(tweet)


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
        print("Today is not a teaching day")
        return False


if __name__ == '__main__':
    str_time = time.time()
    run()
    print(f"Usage time: {time.time() - str_time}")
