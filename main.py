import datetime
from pysenal import *
import pandas as pd
import json
from openai import OpenAI
import re
import numpy as np
from prompt import *
from util import *
import json
from fuzzywuzzy import process
import random
import traceback

def extractor_entities(input_text):
    prompt = PROMPT + f'输入{len(examples)+1}: "{input_text}"\n输出{len(examples)+1}: '
    answer = get_gpt_result(prompt)
    try:
        answer = json.loads(answer)
    except:
        print('gpt error: ', answer)
    return answer

def fuzzy_match(nf, t):
    best_match = process.extractBests(nf, t)
    for i in range(1):
        prompt = f'请结合尺寸和特征，判断以下两种事物是否相同。如果某一个没有交代尺寸和特征，则不用考虑尺寸和特征。不用说明理由，直接回答是或否。\n{nf}\n{best_match[i][0]}'
        answer = get_gpt_result(prompt)
        if '是' in answer:
            return best_match[i][0]
    return ''


data = read_jsonline('data/data.jsonl')
db_data = read_json('data/my_db.json')
random.shuffle(data)
data = data[:50]
result = [['联系内容', '地点', '项目', '项目分析']]

for index, d in enumerate(data):
    try:
        print(d)
        parser_answer = extractor_entities(d)
        print('gpt result: ', parser_answer)


        place = parser_answer['地点']
        place = place[0] if not isinstance(place, str) else place
        place = place.replace('行政办公楼', '行政楼')
        place = '其他项目清单' if place not in ['行政楼', '图书馆', '礼堂', '学生宿舍', '2号食堂'] else place
        project = parser_answer['实施项目']
        if not project:
            continue
        need_fuzzy = []
        matched_result = {}

        for p in project:
            # sql精确匹配
            sql = f'SELECT * FROM project WHERE location="{place}" AND projectName="{p}"'
            print(sql)
            db_row = option_database(sql)
            print(db_row)
            if not db_row:
                need_fuzzy.append(p)
            else:
                matched_result[p] = list(db_row[0])[-1]

        # 模糊匹配
        fuzzy_data = db_data[place]
        for nf in need_fuzzy:
            print('fuzzy mathch: ', nf)
            fuzzy_result = fuzzy_match(nf, list(db_data[place].keys()))
            print(fuzzy_result)
            price = db_data[place].get(fuzzy_result, 0)
            if price:
                matched_result[nf] = price
            print(price)
        print('------------------------------------------------------')
        print(matched_result)

        analyse = []
        sub_result = [d, place, project]

        # 大模型进行判断
        for k, v in matched_result.items():
            prompt = f'请计算{k}在“{d}”中的价格与{v}之间的差价。不要推理过程，直接输出结果。如果没有差价，则输出None'
            answer = get_gpt_result(prompt)

            if answer == 'None':
                analyse.append(f'{k} 没有提到价格')
                continue
            else:
                try:
                    answer = float(answer)
                    if answer > 1000:
                        analyse.append(f'{k} 与数据库内的价格相差大于1000，注意控制费用。')
                    else:
                        analyse.append(f'{k} 与数据库内的价格相差{answer}，注意实际费用支出。')
                except:
                    print(f'{k} 没有提到价格')

        # 没有匹配到价格的工程
        remain_project = [p for p in project if p not in matched_result.keys()]
        for rp in remain_project:
            analyse.append(f'{rp} 没有匹配到库中的价格。可能涉及范围更大的非单项工程改变，注意控制费用。')
        sub_result.append(analyse)
        result.append(sub_result)
    except:
        print(str(traceback.format_exc()))
        print(sub_result)
    print(f'================================{index}=======================================')
write_excel(result, 'random_test_50.xlsx')
