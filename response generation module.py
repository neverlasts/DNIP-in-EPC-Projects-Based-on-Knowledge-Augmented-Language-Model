import datetime

from util import *
import itertools
from fuzzywuzzy import process
import traceback
import datetime



data = read_jsonline('data/step_two_result.jsonl')
result = []
for i, d in enumerate(data):
    print(f'{i}/ {len(data)}: {datetime.datetime.now()}')
    text = d[0].replace('\n', '')
    if not d[2]:
        continue

    mr_result = []
    for mr in d[2]:
        print(mr)
        print('=====================================================')
        project_pre_name = mr[0][0] if mr[0][0] else '物体'
        project_pre_price = mr[0][-2] if mr[0][-2] else 0
        project_pre_unit = mr[0][-1] if mr[0][-1] else ''

        project_pro_name = mr[1][0] if mr[0][0] else '物体'
        project_pro_price = mr[1][-2] if mr[1][-2] else 0
        project_pro_unit = mr[1][-1] if mr[1][-1] else ''

        if mr[0][0] and mr[1][0]:
            if not mr[0][-2] or not mr[1][-2]:
                mr_result.append([mr[0][0], mr[1][0], project_pre_price, project_pro_price, project_pre_unit,
                               project_pro_unit, f'缺少价格'])
                continue

        xishu = -1 if mr[0][0] and not mr[1][0] else 1

        try:
            prompt = f'“{project_pre_name}”的价格是{project_pre_price}元，“{project_pro_name}”的价格是{project_pro_price}元，如果价格有变化，则输出差价。不要说出推理过程，直接输出数值结果。'
            answer = get_gpt_result(prompt)
            print(prompt)
            print(answer)
            answer = answer.replace('差价为', '')
            answer = answer.replace('元', '')
            price_delta = float(answer)
            if price_delta == 0:
                mr_result.append([mr[0][0], mr[1][0], project_pre_price, project_pro_price, project_pre_unit, project_pro_unit, f'差价是：{price_delta}'])
                continue

            prompt = f'{project_pre_name}的价格在下面句子中发生了变化：\n{text}\n请判断这是否是由于业主要求/监理指令？不用输出推理过程，直接回答是或否。'
            answer = get_gpt_result(prompt)
            is_onwer_responsibility = True if '是' in answer else False
            can_claim = True if len(d[1]) > 1 else False

            if price_delta > 1000 and len(d[1]) > 1:
                mr_result.append([mr[0][0], mr[1][0], project_pre_price, project_pro_price, project_pre_unit, project_pro_unit, f'差价是：{xishu * price_delta}，需要注意控制费用', is_onwer_responsibility, can_claim])
            else:
                mr_result.append([mr[0][0], mr[1][0], project_pre_price, project_pro_price, project_pre_unit, project_pro_unit, f'差价是：{xishu * price_delta}', is_onwer_responsibility, can_claim])
        except:
            print('error: ', traceback.format_exc())
    result.append([d[0], d[1], mr_result])

write_jsonline('data/step_three_result.jsonl', result)
write_excel(result, 'data/step_three_result.xlsx')
