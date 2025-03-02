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
    prompt = PROMPT + f'输入{len(examples) + 1}: "{input_text}"\n输出{len(examples) + 1}: '
    answer = get_gpt_result(prompt)
    try:
        start_index = answer.index("{")
        end_index = answer.rindex("}") + 1
        extracted_string = answer[start_index:end_index]
        answer = json.loads(extracted_string)
    except:
        print('gpt error: ', answer)
    return answer


data = read_excel('data/新输入.xlsx')[:2]
data = [d[0] for d in data]
# data = read_jsonline('data/data.jsonl')
result = [['联系内容', '地点', '改变前后的材料']]
result_jsonl = []
for index, d in enumerate(data):
    try:
        print(f'{index} / {len(data)}')
        parser_answer = extractor_entities(d)
        place = []
        for p in parser_answer['地点']:
            if '学生宿舍' in p:
                place.append('学生宿舍')
                continue
            if p == '行政办公楼':
                place.append('行政楼')
                continue
            if p not in ['行政楼', '图书馆', '礼堂', '学生宿舍', '2号食堂']:
                place.append('其他项目清单')
            else:
                place.append(p)

        res = [d, place, parser_answer['改变前后的材料']]
        result.append(res)
        result_jsonl.append(res)
        print(d)
        print(place)
        print(parser_answer['改变前后的材料'])
        input()
    except:
        print('gpt error: ', traceback.format_exc())
        continue

write_excel(result, 'data/step_one_result.xlsx')
write_jsonline('data/step_one_result.jsonl', result_jsonl)
