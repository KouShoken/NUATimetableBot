import inspect
import re
import time
from datetime import datetime
from pathlib import Path
from string import Template

from job import get
from job.get import NUA, TimeList, tokyo_timestamp


class Story:

    @staticmethod
    def get_patten(values):
        stack = inspect.stack()
        caller_function_name = stack[1].function

        file_path = Path(f"bot/stories/{caller_function_name}.txt").resolve()

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

    @staticmethod
    def now_format_period(current_period):
        """
        根据时间戳生成当前的限数和时段 (午前 or 午後)
        """

        # 根据时间判断是午前还是午後
        parts_of_day = "午前" if current_period < 2 else "午後"

        # 返回格式化后的时段信息
        return f"{parts_of_day}{current_period}限"

    @staticmethod
    def now_format_timetable(data):
        """
        格式化课程表信息为以下格式:
        [文芸]
        思想の歴史 ー 山下 洪文
        マンガ演習Ⅱ ー あおき てつお
        マンガ演習Ⅱ ー こにし 真樹子
        """
        # 创建字典用于按科目分类课程
        class_table = {}

        # 遍历数据
        for entry in data:
            subject = entry['subjectAffiliation']
            course = Story.clean_subject_title(entry['subjectName'])  # 清理课程标题
            teacher = Story.clean_subject_title(entry['teacherCharge'])  # 清理教师名称

            # 如果科目还未添加到表中，初始化它
            if subject not in class_table:
                class_table[subject] = []
            # 添加课程和教师信息
            class_table[subject].append((course, teacher))

        # 格式化输出
        result = ""
        for subject, courses in class_table.items():
            result += f"[{subject}]\n"
            for course, teacher in courses:
                result += f"{course} ー {teacher}\n"
            result += "\n"

        return result.strip()
