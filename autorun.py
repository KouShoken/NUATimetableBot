# 运行任务调度
from run import *
from dotenv import load_dotenv

load_dotenv()


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


if __name__ == "__main__":
    schedule_limited_time_tasks()

    # 让调度器一直运行
    while True:
        if run():
            schedule.run_pending()
            time.sleep(10)
        else:
            time.sleep(60 * 60 * 24)
