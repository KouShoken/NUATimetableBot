import inspect
import re
import time
from datetime import datetime
from pathlib import Path
from string import Template

from bot import x
from job.get import NUA, TimeList


class Story:
    MAX_TWEET_LENGTH = 280  # 假设每条推文的最大字数限制为140

    @staticmethod
    def __get_patten(values):
        stack = inspect.stack()
        caller_function_name = stack[1].function

        file_path = Path(f"./stories/{caller_function_name}.txt").resolve()

        # open template file
        with open(file_path, encoding='utf-8') as file:
            # replace template
            template = Template(file.read())
            return template.safe_substitute(values)

    @staticmethod
    def clean_subject_title(text):
        # 去除特殊符号 '※' 后面的内容
        text = text.split('※')[0]

        # 替换全角空格为半角空格
        text = text.replace('\u3000', ' ')

        # 使用正则表达式去除括号（全角和半角）及括号内的内容
        text = re.sub(r'[\(\（].*?[\)\）]', '', text)

        # 去掉多余的前后空格
        return text.strip()

    def split_into_tweets(self, content):
        """根据最大推文长度将内容分割为多个推文"""
        tweets = []
        current_tweet = ""

        for line in content.split("\n"):
            if len(current_tweet) + len(line) + 1 > self.MAX_TWEET_LENGTH:
                tweets.append(current_tweet + "（続）")
                current_tweet = line + "\n"
            else:
                current_tweet += line + "\n"

        if current_tweet:  # 添加最后一条推文
            tweets.append(current_tweet.strip())

        return tweets

    def now_class(self, timestamp=time.time()):
        """　午前2限 #日芸はどんな授業してる？ """

        time_table = TimeList().get_realtime_class(timestamp=timestamp)

        # 整理
        class_table = {}
        for c in time_table:
            if c['subjectAffiliation'] not in class_table:
                class_table[c['subjectAffiliation']] = [(c['subjectName'], c['teacherCharge'])]
            else:
                class_table[c['subjectAffiliation']] += [(c['subjectName'], c['teacherCharge'])]

        # 外国語/体育/芸教の適正処理
        foreign_language, pe, ae, te, gg = [], [], [], [], []

        if "外国" in class_table:
            foreign_language = class_table["外国"]
            del class_table["外国"]
        if "体育" in class_table:
            pe = class_table["体育"]
            del class_table["体育"]
        if "芸教" in class_table:
            ae = class_table["芸教"]
            del class_table["芸教"]
        if "教職" in class_table:
            te = class_table["教職"]
            del class_table["教職"]
        if "学芸" in class_table:
            gg = class_table["学芸"]
            del class_table["学芸"]

        # 格式化输出并存储到 result_str 中
        context = ""
        for subject, courses in class_table.items():
            context += f"[{subject}]\n"
            for course, teacher in courses:
                # 使用 clean_text 函数处理课程名和老师名
                clean_course = self.clean_subject_title(course)
                clean_teacher = self.clean_subject_title(teacher)
                context += f"{clean_course} ー {clean_teacher}\n"

        subjects = self.__get_patten({
            "parts_of_day": "午前" if datetime.fromtimestamp(timestamp).hour < 12 else "午後",
            "period": NUA().get_period(timestamp),
            "context": context
        })

        # 使用字典合并相同的课程
        course_dict = {}

        # 遍历所有的课程数据
        for subject_courses in (foreign_language, pe, ae, te, gg):
            for course, teacher in subject_courses:
                # 使用 self.clean_subject_title 清理课程名和教师名
                clean_course = self.clean_subject_title(course)
                clean_teacher = self.clean_subject_title(teacher)

                # 合并相同的课程
                if clean_course in course_dict:
                    course_dict[clean_course].append(clean_teacher)
                else:
                    course_dict[clean_course] = [clean_teacher]

        # 拼接结果
        others = ""
        for course, teachers in course_dict.items():
            # 将教师名用逗号分隔，拼接到最终字符串
            others += f"{course} ー {', '.join(teachers)}\n"

        # 拆分subjects和others为多个推文
        tweets_subjects = self.split_into_tweets(subjects)
        tweets_others = self.split_into_tweets(others)

        return tweets_subjects, tweets_others


if __name__ == '__main__':
    story = Story()
    tweets_subjects, tweets_others = story.now_class()

    # 输出拆分后的推文
    for tweet in tweets_subjects:
        print(tweet)
        print("------------")
    for tweet in tweets_others:
        print(tweet)
        print("------------")

    # 测试推送
    bot = x.Bot()

    # 示例推文内容

    # 认证 Twitter API
    api = bot.authenticate_twitter()

    # 发送连发推文
    bot.send_tweets(api, tweets_subjects + tweets_others)
