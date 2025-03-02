# coding=utf8
import sqlite3


# 创建文件夹
def createDB():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    '''
    location 类型  
    projectName 项目名称
    feature 项目特征
    unit 计量单位
    price 综合单价
    '''

    sql = '''
           CREATE TABLE IF NOT EXISTS project(
               location TEXT ,  
               projectName TEXT ,
               feature TEXT,
               unit TEXT,
               price TEXT
           );
        '''
    cursor.execute(sql)

    cursor.close()
    conn.close()


if __name__ == '__main__':
    createDB()
