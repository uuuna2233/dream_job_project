''' 將蒐集完畢的職缺放入 Tableau 進行分析，其中 skill 欄位需作進一步處理 (計算不同 skill 出現頻次) '''

import pymysql
from sqlalchemy import create_engine
import pandas as pd


''' 連接資料庫查詢轉為df '''

def con_sql(db,sql):
    db = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="root", db='dream', charset="utf8",use_unicode = True)
    cursor = db.cursor()
    cursor.execute(sql)
    cursor.fetchall()
    df = pd.read_sql(sql,db)
    db.close()
    return df


def skillclear(jobcat):

    db = 'dream'
    sql = f'SELECT joburl,jobcat,skill FROM job where jobcat ="{jobcat}";'
    df = con_sql(db,sql)
    
    df['skill'].replace(' / ', '/')
    df_skill = df['skill'].str.split('/', expand=True)
    df_skill = df_skill.stack()
    df_skill = df_skill.reset_index(level=1, drop=True).rename('skill1')
    df_new = df.drop(['skill'], axis=1).join(df_skill)


    ''' #新 datafrrame 匯入新 table '''

    DB_HOST = 'dream.127.0.0.1'
    DB_PORT = '3306'
    DATABASE = 'dream'
    DB_USER = 'root'
    DB_PASS = 'root'

    connect_info = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE) 
    engine = create_engine(connect_info)

    try:
        pd.io.sql.to_sql(df_new,"skillcount",engine,index=False,if_exists='append')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    f = open('jobcat_8.txt',"r",encoding="utf-8")
    for line in f.readlines():
        skillclear(line.strip())
    f.close()