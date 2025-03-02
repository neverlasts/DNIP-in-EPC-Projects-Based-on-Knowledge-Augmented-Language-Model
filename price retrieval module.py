# coding=utf8
import re
import sqlite3
import difflib
import jieba


def string_similarity(str1, str2):
    matcher = difflib.SequenceMatcher(None, str1, str2)

    # 计算两个字符串的相似度
    similarity = matcher.ratio()
    return similarity


def ar_json(data):
    print('最终结果')
    # print(data)


if __name__ == '__main__':
    # text = input('请输入地点和名称，中间中文分号隔开：')
    # text = '工程改变地点：学生宿舍；真正改变的分项工程名称：600*600地砖，800*800地砖'
    # text = '工程改变地点：学生宿舍；真正改变的分项工程名称：无机涂料顶棚，600*600硅钙板吊顶'
    # text = '工程改变地点：图书馆；真正改变的分项工程名称：门联窗'
    text = '工程改变地点：行政楼；工程改变内容名称：1.2厚三元乙丙橡胶防水卷材，1.5厚聚氨酯防水涂膜，3.0厚SBS改性沥青防水卷材。'
    arr = text.split('；')
    print(arr)
    location = arr[0].split('：')[-1]
    feature = arr[-1].split('：')[-1]
    feature = feature.replace('\ue00a', ' ').replace('\ue009', ' ').replace('\ue00b', ' ').replace('\n', '').replace(
        ' ', '')
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    if '，' in feature:
        fe = feature.split('，')
    else:
        fe = feature.split(',')

    total_data = []
    for fea in fe:
        print(fea, '--------------')
        fea1 = fea.replace('*', '').replace('.', '').replace('。', '')
        fea1 = re.sub(r'\d+', '', fea1)
        print(fea1)
        sql = f'''
               select * from project where location = '{location}' and (feature = '{fea}' or projectName = '{fea}')
           '''

        cursor.execute(sql)
        rows = cursor.fetchall()

        if len(rows) <= 0:
            sql = f'''
                    select * from project where location = '其他项目清单' and feature = '{fea}'
                '''
            cursor.execute(sql)
            rows = cursor.fetchall()
            # 如果其他项目里面都没有的话进行模糊查询
            if len(rows) <= 0:
                # 第一步通过地点查询数据后模糊查询
                sql = f'''
                    select * from project where location = '{location}'
                '''
                cursor.execute(sql)
                rows = cursor.fetchall()
                s_data = []
                for ii in rows:
                    if fea in ii[2]:
                        s_data.append(ii)

                if len(s_data) <= 0:
                    mh_data = []
                    for ii in rows:
                        res = string_similarity(ii[2], fea)
                        if res > 0 and fea in ii[2]:
                            mh_data.append(ii)
                    # 如果当前地点下匹配不到
                    sql = f'''
                        select * from project where location = '其他项目清单'
                    '''
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    for ii in rows:
                        res = string_similarity(ii[2], fea)
                        if res > 0 and fea in ii[2]:
                            mh_data.append(ii)

                    if len(mh_data) <= 0:
                        sql = f'''
                            select * from project where location = '{location}'
                        '''
                        cursor.execute(sql)
                        rows = cursor.fetchall()
                        s_data = []
                        for ii in rows:
                            if fea in ii[2]:
                                s_data.append(ii)

                        if len(s_data) <= 0:
                            mh_data1 = []
                            for ii in rows:
                                res = string_similarity(ii[2], fea)
                                if res > 0 and fea1 in ii[2]:
                                    mh_data1.append(ii)
                            if len(mh_data1) <= 0:
                                sql = f'''
                                   select * from project where location = '其他项目清单'
                                '''
                                cursor.execute(sql)
                                rows = cursor.fetchall()
                                for ii in rows:
                                    res = string_similarity(ii[2], fea)
                                    if res > 0 and fea1 in ii[2]:
                                        mh_data1.append(ii)
                            print(mh_data1, '-6-')
                            ar_json(mh_data1)
                            total_data = total_data + mh_data1
                        else:
                            print(s_data, '-5-')
                            ar_json(s_data)
                            total_data = total_data + s_data
                    else:
                        print(mh_data, '-4-')
                        ar_json(mh_data)
                        total_data = total_data + mh_data
                else:
                    print(s_data, '-3-')
                    ar_json(s_data)
                    total_data = total_data + s_data
            else:
                print(rows, '-2-')
                ar_json(rows)
                total_data = total_data + rows
        else:
            print(rows, '-1-')
            ar_json(rows)
            total_data = total_data + rows

    # 最终的数据
    _t_data = []
    for a in total_data:
        print(a)
        _t_data.append(
            {
                '地点': a[0],
                '项目名称': a[1],
                '项目特征': a[2],
                '计量单位': a[3],
                '综合单价(元)': a[4],

            }
        )
    print(_t_data)
