from typing import Dict
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import json
import re
import datetime

# start_date = datetime.date(2022, 9, 5)
# today = datetime.date(2022,9,10)
# today_weekday = datetime.date.today().isocalendar()[2]
# print(today_weekday)

def parse_weeks(s):
    # case1: 3,5,8-9周 
    # case2: 4,10周 
    # case3: 2-5,7-12周

    l = s.split(',')
    res = []

    for i in l:
        # check if there is '-'
        if '-' in i:
            tmp = i.split('-')
            start_week = int(tmp[0])
            try:
                end_week = int(tmp[1])
            except:
                end_week = int(tmp[1].split("周")[0])
            res.extend(range(start_week, end_week+1))
        else:
            try:
                week = int(i)
            except:
                week = int(i.split("周")[0])

            res.append(int(week))
    return res
    

def parse_detail_info(s) -> Dict:
    if not s:
        return {}
    info_pattern = re.compile(r'(.*)  (.*)周.(.*)')
    info = info_pattern.match(s)
    if info:

        res = {
            "class_name": info.group(1),
            "weeks": parse_weeks(info.group(2)),
            "classroom": info.group(3)
        }
        return res
    else:
        return None
    

def parse_baseinfo(s):
    if not s:
        return None
    tmp = s.split("/")
    tmp = [t.strip() for t in tmp]
    tmp.pop(0)
    print(tmp)
    for i in range(len(tmp)):
        tmp[i] = parse_detail_info(tmp[i])


    return tmp

def generate_json(filepath):
    html_filename = filepath
    html1 = BeautifulSoup(open(html_filename), 'html.parser')
    html2 = html1.prettify()

    df1 = pd.read_html((html2))[2]
    print(df1)

    df1.columns = [i for i in range(len(df1.columns))]
    df1.drop(df1.index[0], inplace=True)
    df1.drop(df1.columns[0], axis=1, inplace=True)
    dic = df1.to_json()
    j  = json.loads(dic)

    ks = j.keys()
    for k in ks:
        for week in j[k].keys():
            j[k][week] = parse_baseinfo(j[k][week])

    
    return j

def get_classes_by_week(week, filepath):
    j = generate_json(filepath)
    week_cnt = week
    res = {}
    for week in range(1,8):
        # print("=======================week {}===星期{}=====================".format(week_cnt, week))
        # print("今天是星期{}".format(week))
        tmp_weekday = "星期{}".format(week)
        res[tmp_weekday] = []
        today_class = j[str(week)]
        for rank in range(1,6):
            # print("第{}节课".format(rank))
            classes = today_class[str(rank)]
            if not classes:
                # print("没有课")
                continue
            for c in classes:
                if not c:
                    continue
                c_name = c["class_name"]
                c_weeks = c["weeks"]
                c_classroom = c["classroom"]
                if week_cnt in c_weeks:
                    print("{} {} {}".format(c_name, c_weeks, c_classroom))
                    res[tmp_weekday].append("第{}节课 {} {}".format(rank, c_name, c_classroom))
                    
    # format the result
    tmp_res = ""
    for week in res.keys():
        tmp_res += week + ":\n"
        for c in res[week]:
            tmp_res += c + "\n"
        tmp_res += "\n"
    return tmp_res
    

# # if __name__ == "__main__":
# #     now_week = 1
# #     j = generate_json("/app/data/test.html")
#     for week_cnt in range(0, 18):
            
#         for week in range(1,8):
#             print("=======================week {}===星期{}=====================".format(week_cnt, week))
#             print("今天是星期{}".format(week))
#             today_class = j[str(week)]
#             for rank in range(1,6):
#                 print("第{}节课".format(rank))
#                 classes = today_class[str(rank)]
#                 if not classes:
#                     # print("没有课")
#                     continue
#                 for c in classes:
#                     c_name = c["class_name"]
#                     c_weeks = c["weeks"]
#                     c_classroom = c["classroom"]
#                     if week_cnt in c_weeks:
#                         print("{} {} {}".format(c_name, c_weeks, c_classroom))