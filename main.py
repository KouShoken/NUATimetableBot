import schedule
import time
from datetime import datetime, timedelta

from bot import x
from bot.story import Story
from job.get import NUA


def send():
    story = Story()
    tweets_subjects, tweets_others = story.now_class()

    # 测试推送
    bot = x.Bot()

    # 认证 Twitter API
    api = bot.authenticate_twitter()

    # 发送连发推文
    bot.send_tweets(api, tweets_subjects + tweets_others)


# 计算每个限的前 10 分钟时间，并设置定时任务
def schedule_limited_time_tasks():
    nua = NUA()

    for i, (start_hour, start_minute, end_hour, end_minute) in enumerate(nua.class_schedule, start=1):
        # Convert the class start time to a datetime object
        limit_time = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        # Calculate the task time, 10 minutes before the class starts
        task_time = limit_time - timedelta(minutes=10)

        # Schedule the task
        schedule.every().day.at(task_time.strftime("%H:%M")).do(send)
        print(f"Scheduled task for {i}限 at {task_time.strftime('%H:%M')}")


def is_today_teaching(filepath):
    # 读取日期文件
    with open(filepath, encoding="utf-8-sig") as file:
        dates = file.readlines()
    # 去除换行符并转换为 datetime 对象，只考虑月日
    dates = [datetime.strptime(date.strip(), "%m月%d日") for date in dates]

    today = datetime.now()

    # 如果今天是周日，返回 False
    if today.weekday() == 6:  # 周日对应的 weekday() 值为 6
        return False

    # 检查今天的日期是否在文件中的日期列表里
    today_no_year = today.replace(year=1)  # 忽略年份，只考虑月日
    return today_no_year in dates


# 运行任务调度
if __name__ == "__main__":
    schedule_limited_time_tasks()

    # 让调度器一直运行
    while True:
        if is_today_teaching("teaching_dates.csv"):
            schedule.run_pending()
            time.sleep(10)
        else:
            print("Today is not a teaching day, sleeping for 24 hours.")
            time.sleep(24 * 60 * 60)
