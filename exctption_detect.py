from util import *


def detect(my_data):
    # id name feature unit price
    error_data = []
    print(f'    {len(my_data)}')
    total = len(my_data) * (len(my_data) - 1) / 2
    count_num = 1

    for i in range(len(my_data)):
        for j in range(i+1, len(my_data)):
            print(f'    {count_num} / {total}')
            count_num += 1
            d1 = my_data[i]
            d2 = my_data[j]
            if d1[2] == d[2] and d1[-1] != d2[-1]:
                error_data.append([d1[0], d2[0], '1'])
                continue
            if d1[-1] == d2[-1]:
                prompt = f'忽略尺寸，请判断下面两种材料是否是同一型号。不要输出推理内容，直接回答是或否。{d1[2]}\n{d2[2]}\n'
                answer = get_gpt_result(prompt)
                if '否' in answer:
                    error_data.append([d1[0], d2[0], '3'])
                    continue
            if abs(d1[-1] - d2[-1]) > 0.3 * min(d1[-1], d2[-1]):
                prompt = f'请判断下面两种材料的尺寸是否一致。不要输出推理内容，直接回答是或否。{d1[2]}\n{d2[2]}\n'
                answer = get_gpt_result(prompt)
                if '是' in answer:
                    error_data.append([d1[0], d2[0], '2'])
                    continue
    return error_data

# name feature unit price
origin_data = read_excel('data/exception_data.xlsx')[1:]
print(len(origin_data))

data = {}
for d in origin_data:
    data.setdefault(d[1], [])
    data[d[1]].append(d)

result = []
count = 1
for k, v in data.items():
    print(f'{count} / {len(data)}')
    error_data = detect(v)
    result.extend(error_data)
    count += 1
write_excel(result, 'data/exception_result.xlsx')

