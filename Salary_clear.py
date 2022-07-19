import pymysql
import pandas as pd
import numpy as np
import datetime


class SalaryClear:
    def process(all_data):
        
        feature_list=['minsalary','maxsalary']
        
        for col in feature_list:
    
            ulimit=np.percentile(all_data[col].values.astype(np.int64), 75) 
            llimit=np.percentile(all_data[col].values.astype(np.int64), 25)
            
            # 將超出1.5倍離群值移除
            n=1.5
            IQR=ulimit-llimit
            
            # # outlier=ulimit±n*IQR
            all_data=all_data[all_data[col]<ulimit+n*IQR]
            all_data=all_data[all_data[col]>llimit-n*IQR]
            
        return all_data
    
    
    ''' 連接資料庫查詢轉為df '''
    
    def con_sql(db,sql):
        db = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="root", db="dream",  charset="utf8", use_unicode = True)
        cursor = db.cursor()
        cursor.execute(sql)
        cursor.fetchall()
        df = pd.read_sql(sql,db)
        db.close()
        return df
    
    def newsalary(jobcat):
        
        date_now = datetime.date.today()
        date_30days = date_now - datetime.timedelta(30)
    
        db = 'dream'
        sql = f'SELECT jobtitle,jobcat,minsalary,maxsalary FROM `job` where `jobcat` = "{jobcat}" and (`salary` like"%月%" or salary like "month" or salary like "%年%" or salary like "%year%") and (`updatetime` > {date_30days});'
        df = SalaryClear.con_sql(db,sql)
        # print(df.describe())
    
    
        ''' 數據處理 '''
    
        ##去除薪資為0欄位##
        
        df.drop(df.loc[df['minsalary']==0].index, inplace=True)
        df.drop(df.loc[df['maxsalary']==0].index, inplace=True)        
        
        data_new = SalaryClear.process(df)
        max50 = data_new.describe()['maxsalary']['50%']
        min50 = data_new.describe()['minsalary']['50%']
        
        return max50, min50

"""
if __name__ == '__main__':
    f = open(r'jobcat_8.txt',"r",encoding="utf-8")
    for line in f.readlines():
        max50, min50 = SalaryClear.newsalary(line.strip())
        print('max50', max50)
        print('min50', min50)
    f.close()
    
"""