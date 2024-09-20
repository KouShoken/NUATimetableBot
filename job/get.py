import os
import time
import time as t
from datetime import datetime

import pytz
import requests


def tokyo_timestamp():
    # 获取东京时区
    tokyo_tz = pytz.timezone('Asia/Tokyo')

    # 获取当前东京时间
    tokyo_time = datetime.now(tokyo_tz)

    # 返回时间戳
    return tokyo_time.timestamp()


class TimeList:
    """ Time table api requests """

    @staticmethod
    def __get(url, data=None):
        if data is None:
            data = []

        return requests.get(url, params=data)

    def all(self):
        """Get a full timetable"""
        url = "https://nichigei-timetable.com/api/timetable/list?sortName=periodSortCode&studentType=1&allSearch%5B0%5D=ALL%E6%A4%9C%E7%B4%A2&count=100&studentTypeHidden=1"
        return self.__get(url=url).json()

    def search(self, studentYear, subjectAffiliation,
               dayWeek, semester, subjectAffiliationExcept=range(9, 16), period=range(1, 7)
               ):
        url = "https://nichigei-timetable.com/api/timetable/list"
        data = {
            "studentYear": studentYear,
            "subjectAffiliation": subjectAffiliation,
            "dayWeek": dayWeek,
            "semester": semester
        }

        for key in range(len(subjectAffiliationExcept)):
            d = subjectAffiliationExcept[key]
            data[f" subjectAffiliationExcept[{key}]"] = d

        for key in range(len(period)):
            d = period[key]
            data[f" period[{key}]"] = d

        return self.__get(url, data).json()

    def get_realtime_class(self, timestamp=tokyo_timestamp(), subjectAffiliation=0):
        """Get the class on teaching"""
        now_period = NUA().get_period(timestamp)

        if now_period == 0:  # 時間外
            return []

        return self.search(
            studentYear=0,
            subjectAffiliation=0,
            dayWeek=datetime.fromtimestamp(timestamp).weekday() + 1,
            period=[now_period],
            semester=NUA().check_semester(timestamp),
        )


class NUA:
    """ NUA schedule """

    def __init__(self):
        self.class_schedule = [
            (9, 0, 10, 30),
            (10, 30, 13, 0),
            (13, 0, 14, 30),
            (14, 30, 16, 10),
            (16, 10, 18, 0),
            (18, 0, 19, 30)
        ]

        this = datetime.fromtimestamp(tokyo_timestamp())
        self.sta_semester1 = datetime(this.year, 4, 1)
        self.end_semester1 = datetime(this.year, 8, 30)
        self.sta_semester2 = datetime(this.year, 9, 1)
        self.end_semester2 = datetime(this.year + 1, 2, 1)

    def get_period(self, timestamp=tokyo_timestamp()):
        # 获取东京时区
        tokyo_tz = pytz.timezone('Asia/Tokyo')

        # 将时间戳转换为东京时间
        t = datetime.fromtimestamp(timestamp, tokyo_tz)

        hour, minute = t.hour, t.minute

        for i, (start_h, start_m, end_h, end_m) in enumerate(self.class_schedule):
            if (start_h, start_m) <= (hour, minute) <= (end_h, end_m):
                return i + 1

        return 0

    def check_semester(self, timestamp):

        date = datetime.fromtimestamp(timestamp)

        if self.sta_semester1 <= date <= self.end_semester1:
            return 1
        elif self.sta_semester2 <= date <= self.end_semester2:
            return 2
        else:
            return 0


if __name__ == '__main__':
    t1 = TimeList().get_realtime_class(timestamp=1727229330)
    print(t1)
