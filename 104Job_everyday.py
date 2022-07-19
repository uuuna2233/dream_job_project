''' 此為定期更新版本(更新頻率: 暫定每日更新)，若為第一次蒐集「全部」資料進資料庫，將 get url 參數改為 'isnew': '30' 即可 '''

# !pip install fuzzywuzzy
# !pip install python-Levenshtein  # 加速字串匹配的庫
# 需先到原文件下載對應版本，並pip install wheel，再進到python-Levenshtein所在目錄直接安裝
# !pip install fake_useragent

import time
import random
import requests
import pandas as pd
from DB_initial import DB
import re
from fake_useragent import UserAgent
from fuzzywuzzy import process
from Salary_clear import SalaryClear

ua = UserAgent()

class Job104Spider():
    def search(self, keyword, filter_params=None, sort_type='符合度', is_sort_asc=False):
        """搜尋職缺"""
        jobs = []
        total_count = 0

        url = 'https://www.104.com.tw/jobs/search/list'
        query = f'ro=0&kwop=7&keyword={keyword}&expansionType=area,spec,com,job,wf,wktm&mode=s&jobsource=2018indexpoc'
        if filter_params:
            # 加上篩選參數，要先轉換為 URL 參數字串格式
            query += ''.join([f'&{key}={value}' for key, value, in filter_params.items()])

        headers = {
            'User-Agent': ua.chrome,
            'Referer': 'https://www.104.com.tw/jobs/search/',
        }

        # 加上排序條件
        sort_dict = {
            '符合度': '1',
            '日期': '2',
            '經歷': '3',
            '學歷': '4',
            '應徵人數': '7',
            '待遇': '13',
        }
        sort_params = f"&order={sort_dict.get(sort_type, '1')}"
        sort_params += '&asc=1' if is_sort_asc else '&asc=0'
        query += sort_params

        page = 1
        while page <= 100:  # 最大頁數100
            params = f'{query}&page={page}'
            r = requests.get(url, params=params, headers=headers, timeout=(6,10))  # Fix requests.exceptions.ConnectTimeout
            if r.status_code != requests.codes.ok:
                print('搜尋職缺請求失敗', r.status_code)
                data = r.json()
                print(data['status'], data['statusMsg'], data['errorMsg'])
                continue

            data = r.json()
            total_count = data['data']['totalCount']
            jobs.extend(data['data']['list'])

            if (page == data['data']['totalPage']) or (data['data']['totalPage'] == 0):
                break
            page += 1
            time.sleep(random.uniform(1, 2))

        return total_count, jobs


    def search_job_id(self, job_data):
        """取得職缺id"""
        job_url = f"https:{job_data['link']['job']}"
        
        jobIdList = job_url.split('/job/')[-1].split('?')[0]

        return jobIdList


    def get_job(self, job_id):
        """取得職缺詳細資料"""
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'

        headers = {
            'User-Agent': ua.chrome,
            'Referer': f'https://www.104.com.tw/job/{job_id}'
        }

        r = requests.get(url, headers=headers, timeout=(6,10))
        if r.status_code != requests.codes.ok:
            print('取得職缺詳細資料請求失敗', r.status_code)
            print('該職缺 id 為: ', job_id)
            return {}, None
        
        else:
            data = r.json()
            
            try:
                jobLink = f'https://www.104.com.tw/job/{job_id}'
                jobUpdate = data['data']['header']['appearDate']
                # jobIndustry = data['data']['industry']
                jobCompany = data['data']['header']['custName']
                jobTitle = data['data']['header']['jobName'].replace('"', "'")
                # jobCategory = [i['description'] for i in data['data']['jobDetail']['jobCategory']]
                jobSalary = data['data']['jobDetail']['salary']
                jobMax = data['data']['jobDetail']['salaryMax']
                jobMin = data['data']['jobDetail']['salaryMin']                
                jobCity = (f"{data['data']['jobDetail']['addressRegion']}")[:3]
                jobDescription = data['data']['jobDetail']['jobDescription'].replace('"', "'")
                # jobDuty = data['data']['jobDetail']['manageResp']
                # jobTrip = data['data']['jobDetail']['businessTrip']
                # jobPeriod = data['data']['jobDetail']['workPeriod']
                # jobVacation = data['data']['jobDetail']['vacationPolicy']
                # jobStart = data['data']['jobDetail']['startWorkingDay']
                # jobNeedEmp = data['data']['jobDetail']['needEmp']
                jobExp = data['data']['condition']['workExp']
                jobExp = dream_job.jobExpTrans(jobExp)
                # jobEdu = data['data']['condition']['edu']
                # jobMajor = data['data']['condition']['major']
                # jobLanguage = [i['language'] + ': ' + i['ability'] for i in data['data']['condition']['language']]
                jobSpecialty = "/".join([i['description'] for i in data['data']['condition']['specialty']])
                jobOther = data['data']['condition']['other'].replace('"', "'")
                jobWelfare = data['data']['welfare']['welfare'].replace('"', "'")
                # jobContact = [i for i in data['data']['contact'].values() if i not in ('', [], False)]
                
                jobMax, jobMin = dream_job.salaryClean(jobMax, jobMin, jobSalary)
                jobSkill = dream_job.requirements(jobDescription, jobSpecialty, jobOther)
                conformity = len(jobSkill)
                
                jobResult = {
                        '職缺網址': jobLink,
                        '更新日期': jobUpdate,
                        '公司名稱': jobCompany,
                        '工作職稱': jobTitle,
                        '職務類別': keyword,
                        '工作待遇': jobSalary,
                        '最高薪資': jobMax,
                        '最低薪資': jobMin,
                        '上班地點': jobCity,
                        '工作內容': jobDescription,
                        '工作經驗': jobExp,
                        '擅長工具': jobSpecialty,
                        '其他條件': jobOther,
                        '福利制度': jobWelfare,
                        '技能要求': jobSkill}
                        # '系統更新': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
                time.sleep(random.uniform(0, 1))
            
                return jobResult, jobTitle, conformity, jobSalary
            except Exception as e:
                print(e)
                print('該職缺 id 為: ', job_id)
                
                return {}, None, None, None

class DreamJob():
    def requirements(self, jobDescription, jobSpecialty, jobOther):
        """判斷技能要求是否與所學相關"""
        pattern = r'IoT|Linux|Python|MySQL|SQL|API|Hadoop|InfluxDB|ELK|Elastic Search|Logstash|Kibana|Splunk|AWS|Tableau|Qlik|PowerBI|BI​|GCP|Oracle Data Visualization|Big Data|Machine Learning|TensorFlow|Deep Learning|Crawler|Data Collection|Data Modeling|Data Mining|Data Cleaning|Data Visualization|Data Pipeline|Flask|Hive|sqoop|impala|flume|oozie|MongoDB|ETL|ELT|Git|Azure|Algorithm|大數據|資料收集|數據收集|資料建模|數據建模|資料清洗|數據清洗|資料清理|數據清理|視覺化|爬蟲|機器學習|深度學習|資料工程|資料探勘|演算法'
        jobRequired = str([jobDescription] + [jobOther]) + jobSpecialty
        jobSkills = re.findall(pattern, jobRequired, flags=re.I)
        
        # 合併同義詞
        jobSkills=[Sk.replace('mysql', 'sql').replace('powerbi', 'bi').replace('大數據', 'big data').replace('機器學習', 'machine learning').replace('深度學習', 'deep learning').replace('資料收集', 'data collection').replace('數據收集', 'data collection').replace('資料建模', 'data Modeling').replace('數據建模', 'ata Modeling').replace('資料清洗', 'data cleaning').replace('數據清洗', 'data cleaning').replace('資料清理', 'data cleaning').replace('數據清理', 'data cleaning').replace('視覺化', 'data visualization').replace('爬蟲', 'crawler').replace('資料探勘', 'data mining').replace('演算法', 'algorithm') for Sk in jobSkills]
        
        # set: 技能去重 # casefold: 統一為lower case
        jobSkill = set(Sk.casefold() for Sk in jobSkills)
        
        # 移除\u200b
        jobSkill = '/'.join(Sk.replace('\u200b','') for Sk in jobSkill)
        
        return jobSkill
    
    def salaryClean(self, jobMax, jobMin, jobSalary):
        """薪資清洗"""
        
        if "面議" in jobSalary:
            jobMin = 40000
            jobMax = 0
            
        if "以上" in jobSalary:
            jobMax = 0
                
        if "年薪" in jobSalary:
            jobMin = jobMin/12
            if jobMax != 0:
                jobMax = jobMax/12

        return jobMax, jobMin
    
    def jobCategory(self, keyword):
        """判斷職務類別"""     
        
        try:
            i = words2.index(keyword)
            if 12 >= i >= 0:
                jobCategory = '數據分析師'
            elif 16 >= i >= 13:
                jobCategory = '商業分析師'
            elif 21 >= i >= 17:
                jobCategory = '數據工程師'
            elif 32 >= i >= 22:
                jobCategory = '機器學習工程師'
            elif 40 >= i >= 33:
                jobCategory = '數據庫工程師'
            elif 46 >= i >= 41:
                jobCategory = '研究人員'
            elif 51 >= i >= 47:
                jobCategory = '軟體開發工程師'
            elif 55 >= i >= 52:
                jobCategory = '維運工程師'
            else:
                jobCategory = 'Null'
            
        except:
            # 移除字串中的空白符再判定是否為純英文
            keyword = re.sub(r"\s+", "", keyword)
            if keyword.isalpha() == True:
                if keyword == 'DataAnalyst':
                    jobCategory = '數據分析師'
                elif keyword == 'BusinessAnalyst':
                    jobCategory = '商業分析師'
                elif keyword == 'DataEngineer':
                    jobCategory = '數據工程師'
                elif keyword == 'DataScientist':
                    jobCategory = '機器學習工程師'
                elif keyword == 'DatabaseAdministrator':
                    jobCategory = '數據庫工程師'
                elif keyword == 'SoftwareEngineer':
                    jobCategory = '軟體開發工程師'
                elif keyword == 'OperationEngineer':
                    jobCategory = '維運工程師'
                else:
                    jobCategory = 'Null'
            
            
        return jobCategory

    def jobExpTrans(self, jobExp):
        """將年資需求轉成數值"""
        
        if '不拘' in jobExp:
            jobExp = '0'
            
        else:
            jobExp = re.search(r'\d+',jobExp).group()
            
        return jobExp

if __name__ == "__main__":
    job104_spider = Job104Spider()
    dream_job = DreamJob()

    # cp950' codec can't decode byte 0xe6
    with open('jobsearch.txt','r',encoding="utf-8") as f:
        lines = f.readlines()
        words1 = [word.strip() for word in lines]
        
    with open('jobcategory.txt','r',encoding="utf-8") as f:
        lines = f.readlines()
        words2 = [word.strip() for word in lines]
            
        filter_params = {
            # 'area': '6001001000,6001016000',  # (地區) 台北市,高雄市
            # 's9': '1,2,4,8',  # (上班時段) 日班,夜班,大夜班,假日班
            # 's5': '0',  # 0:不需輪班 256:輪班
            # 'wktm': '1',  # (休假制度) 週休二日
             'isnew': '0',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
            # 'jobexp': '1,3', # (經歷要求) 1年以下,1-3年,3-5年,5-10年,10年以上
            # 'sctp':'M', 'scmin':'40000', # 月薪四萬以上，但月薪與年薪無法同時設定
            # 'scneg':'1', # 包含面議
            # 'newZone': '1,2,3,4,5',  # (科技園區) 竹科,中科,南科,內湖,南港
            # 'zone': '16',  # (公司類型) 16:上市上櫃 5:外商一般 4:外商資訊
            # 'wf': '1,2,3,4,5,6,7,8,9,10',  # (福利制度) 年終獎金,三節獎金,員工旅遊,分紅配股,設施福利,休假福利,津貼/補助,彈性上下班,健康檢查,團體保險
            # 'edu': '1,2,3,4,5,6',  # (學歷要求) 高中職以下,高中職,專科,大學,碩士,博士
            # 'remoteWork': '1',  # (上班型態) 1:完全遠端 2:部分遠端
            # 'excludeJobKeyword': '科技',  # 排除關鍵字
            # 'kwop': '1',  # 只搜尋職務名稱
             'mode': 'l',  # (版面呈現) l:列表, s:摘要
        }
        
        # 不再重複蒐集相同職缺，若不同關鍵字的 ID 未重複，則添加進 jobIDCollect
        jobIDCollect = []
        num = 0
        for keyword in words1:
            total_count, jobs = job104_spider.search(keyword, filter_params=filter_params)
            print(keyword, '職缺總數： ', total_count)
            # print('搜尋結果職缺資料：', jobs)
            
            jobIdList = [job104_spider.search_job_id(job_data) for job_data in jobs]            
            # print('搜尋結果職缺id列表： ', jobIdList)
            num += 1
            if num == 1:
                jobIDCollect = jobIdList
            else:
                for ID in jobIdList:
                    if ID not in jobIDCollect:
                        jobIDCollect.append(ID)
                    else:
                        jobIdList.remove(ID)
                
            # pd.set_option('display.max_columns', None)
            jobList_gold = jobList_silver = pd.DataFrame()
            jobResult_gold = []
            
            if jobIdList != None:
                for job_id in jobIdList:
                    jobResult, jobTitle, conformity, jobSalary = job104_spider.get_job(job_id)
                    if jobResult != {}:
                        # 搜尋如'數據分析'、'軟體工程'會有很多不相關職缺，因此需判定若有提及學到的技能1個以上，方可被納入
                        if conformity >= 1:
                            # 取相似度最高的職務類別(分數需>50，若無則類別判定為原先keyword)，再指到職務類別(群)，並回填 jobResult
                            if process.extractOne(jobTitle, words2)[1] > 50:                                 
                                jobResult['職務類別'] = jobCategory = dream_job.jobCategory(process.extractOne(jobTitle, words2)[0])
                                max50, min50 = SalaryClear.newsalary(jobCategory)
                                if '月薪' in jobSalary or "年薪" in jobSalary:
                                    if jobResult['最高薪資'] == 0:
                                        jobResult['最高薪資'] = max50
                                    jobList_gold = pd.concat([jobList_gold, pd.DataFrame([jobResult])], ignore_index = True)
                                    jobResult_gold.append(jobResult)
                            else:
                                jobResult['職務類別'] = jobCategory = dream_job.jobCategory(keyword)
                                max50, min50 = SalaryClear.newsalary(jobCategory)
                                if '月薪' in jobSalary or "年薪" in jobSalary:
                                    if jobResult['最高薪資'] == 0:
                                        jobResult['最高薪資'] = max50
                                jobList_gold = pd.concat([jobList_gold, pd.DataFrame([jobResult])], ignore_index = True)
                                jobResult_gold.append(jobResult)      
                        else:                        
                            jobList_silver = pd.concat([jobList_silver, pd.DataFrame([jobResult])], ignore_index = True)
                    
            # save to csv
            # upDate = date.today()
        
            # jobList_gold.to_csv('104Crawler_gold_' + upDate.isoformat() + ('.csv'), mode = 'a', header = f.tell()==0, encoding = 'utf_8_sig')
            # jobList_silver.to_csv('104Crawler_silver_' + upDate.isoformat() + ('.csv'), mode = 'a', header = f.tell()==0, encoding = 'utf_8_sig')
        
            # import to mySQL
            db, cursor = DB.db_init()
        
            try:
                with db.cursor() as cursor:
                    for g in jobResult_gold:
                        try:
                            sql = f'''REPLACE INTO `dream`.`job`
                                    (jobtitle,jobcat,joburl,company,city,salary,maxsalary,minsalary,skill,ryear,jd,jr,welfare,source,updatetime) VALUES
                                    ("{g['工作職稱']}","{g['職務類別']}","{g['職缺網址']}","{g['公司名稱']}","{g['上班地點']}","{g['工作待遇']}","{g['最高薪資']}","{g['最低薪資']}","{g['技能要求']}","{g['工作經驗']}","{g['工作內容']}","{g['其他條件']}","{g['福利制度']}","{'104人力銀行'}","{g['更新日期']}")'''
                            
                            cursor.execute(sql)
        
                        except Exception as e:
                            print(e)
                            continue
                db.commit()
        
            finally:
                db.close()
                
        # print('你所想要的夢幻職缺已成功存入csv檔!')
        print('你所想要的夢幻職缺已成功匯入mySQL!')
