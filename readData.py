# coding=utf8
import pandas as pd
import sqlite3


def read():
    df = pd.read_excel('数据.xlsx', engine='openpyxl', sheet_name=None)

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    sql1 = 'delete from project'
    cursor.execute(sql1)
    conn.commit()

    sql = "INSERT OR REPLACE INTO project (location,projectName,feature,unit,price) values (?,?,?,?,?)"
    for sheet_name in df.keys():
        print(sheet_name)
        header = df[sheet_name].columns.tolist()

        for i in df[sheet_name].values:
            if str(i[0]) != 'nan':
                print(i, '+++++++++++')
                b = str(i[1]).replace('\ue00a', ' ').replace('\ue009', ' ').replace('\ue00b', ' ').replace('\n', '').replace(' ', '')
                sql1 = 'select count(*) num from project where location = ? and feature = ?'
                cursor.execute(sql1, (sheet_name, b))
                num = cursor.fetchone()

                if num[0] <= 0:
                    cursor.execute(sql, (sheet_name.replace(' ', ''), i[0], b, i[2], i[3]))
                    conn.commit()

    cursor.close()
    conn.close()


if __name__ == '__main__':
    read()
