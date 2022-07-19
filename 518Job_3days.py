''' 此為定期更新版本(更新頻率: 暫定 3 天一次)，若為第一次蒐集「全部」資料進資料庫，get url 參數改為 al=6 即可 '''

import requests
from lxml import html
from bs4 import BeautifulSoup as bs
import re
from fuzzywuzzy import process
from fake_useragent import UserAgent
from DB_initial import DB
from Salary_clear import SalaryClear


def jobCategory(keyword):
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



def find_job_518(q):
    """搜尋職缺詳情"""
    ua=UserAgent()
    headers = {'user-agent': ua.random}
    
    urllist=[]
    for p in range(page):
        url_site = f'https://www.518.com.tw/job-index-P-{p+1}.html?&ad={q}&al=3'
        res = requests.get(url_site, headers = headers)
        soup = bs(res.text, 'lxml') 
        u = soup.select('li.title.title_518 > a')
        res.close()

    #url
        urls = [i['href'] for i in u]
        for url_result in urls:
            urllist.append(url_result)

    with open(r'jobcategory.txt','r',encoding="utf-8") as f:
        lines = f.readlines()
        words2 = [word.strip() for word in lines]
        
    for url in list(set(urllist)): #利用set去重
        job = requests.get(url, headers=headers)
        tree=html.fromstring(job.text)
        sp = bs(job.text, 'lxml')
        
    #Title
        job_title1 = tree.cssselect('.job-title')
        job_title = job_title1[0].text if job_title1 != [] else 'Null'
            
        if process.extractOne(job_title, words2)[1] > 50:                                 
            jobcat=jobCategory(process.extractOne(job_title, words2)[0])       
        else:
            jobcat=jobCategory(q)

    #date
        date1 = tree.cssselect('time')
        date = date1[0].text if date1 != [] else 'Null'
        if "前" in date:
            job_date = "Null"
        else:
            job_date = date.replace('更新日期:', '')

    #公司
        job_company1 = tree.cssselect('#stickyFeatures h2 span')
        job_company = job_company1[0].text if job_company1 != [] else 'Null'

    #city
        job_city1 = tree.cssselect('.job-location+ span')
        job_city = job_city1[0].text[:3] if job_city1 != [] else 'Null'
        
    #salary
    
        max50, min50 = SalaryClear.newsalary(jobcat)
        job_salary1 = tree.cssselect('.jobItem li:nth-child(1) span')
        job_salary = job_salary1[0].text if job_salary1 != [] else 'Null'
        if "以上" in job_salary:
            if "面議" in job_salary:
                min = 40000
                max = max50
            else:
                a = job_salary.split(" ")
                min = int(a[2].replace(',', ''))
                max = 0
                if "月薪" in job_salary:
                    max = max50
                if "年薪" in job_salary:
                    min = min/12
                    max = max50
        else:
            b = job_salary.split(" ", 4)
            if len(b) == 5:
                min = int(b[2].replace(',', ''))
                max = int(b[4].replace(',', '').replace(' 元', ''))
                if "年薪" in job_salary:
                    min = min/12
                    max = max/12
                if "論件" in job_salary:
                    min = max = 'null'
            elif len(b) == 3:
                min = max = int(b[2].replace(',', ''))
                if "年薪" in job_salary:
                    min = min/12
                    max = max/12
            else:
                min = max = 'null'

    #工作內容描述
        job_description1 = sp.select('.JobDescription p')
        job_description = job_description1[0].text if job_description1 != [] else 'Null'

    #擅長工具
        job_tool1 = sp.select('#content > div:nth-child(2) > div> ul > li:nth-child(8)')
        job_tool = job_tool1[0].text.replace('擅長工具  ', '') if job_tool1 != [] else 'Null'

    #工作技能
        job_sk1 = sp.select('#content > div:nth-child(2) > div> ul > li:nth-child(9)')
        job_sk = job_sk1[0].text.replace('工作技能  ', '') if job_sk1 != [] else 'Null'

    #其他條件jobrequire 
        job_other1 = sp.select('#content > div:nth-child(2) > div> ul > li:nth-child(10)')
        job_other = job_other1[0].text.replace('其他條件  ', '') if job_other1 != [] else 'Null'

    #skill
        pattern = r'IoT|Linux|Python|MySQL|SQL|API|Hadoop|InfluxDB|ELK|Elastic Search|Logstash|Kibana|Splunk|AWS|Tableau|Qlik|PowerBI|BI​|GCP|Oracle Data Visualization|Big Data|Machine Learning|TensorFlow|Deep Learning|Crawler|Data Collection|Data Modeling|Data Mining|Data Cleaning|Data Visualization|Data Pipeline|Flask|Hive|sqoop|impala|flume|oozie|MongoDB|ETL|ELT|Git|Azure|Algorithm|大數據|資料收集|數據收集|資料建模|數據建模|資料清洗|數據清洗|資料清理|數據清理|視覺化|爬蟲|機器學習|深度學習|資料工程|資料探勘|演算法'
        jobRequired = str([job_description] + [job_tool] + [job_sk] + [job_other])
        skills = re.findall(pattern, jobRequired, flags=re.I)
        
        # 合併同義詞
        skills=[Sk.replace('mysql', 'sql').replace('powerbi', 'bi').replace('大數據', 'big data').replace('機器學習', 'machine learning').replace('深度學習', 'deep learning').replace('資料收集', 'data collection').replace('數據收集', 'data collection').replace('資料建模', 'data Modeling').replace('數據建模', 'ata Modeling').replace('資料清洗', 'data cleaning').replace('數據清洗', 'data cleaning').replace('資料清理', 'data cleaning').replace('數據清理', 'data cleaning').replace('視覺化', 'data visualization').replace('爬蟲', 'crawler').replace('資料探勘', 'data mining').replace('演算法', 'algorithm') for Sk in skills]

        conformity = set(sk.casefold() for sk in skills)
        # print('conformity', conformity)
        conlist = list(conformity)
        constr = "/".join(conlist)
        job_skill = constr

    #員工福利
        job_welfare1 = sp.select('.text-box p')
        job_welfare = job_welfare1[0].text if job_welfare1 != [] else 'Null'

    #年資
        job_year1 = sp.select('#content > div:nth-child(2) > div> ul > li:nth-child(5)')
        job_year = job_year1[0].text.replace('工作經驗  ', '') if job_year1 != [] else 'Null'
        if '不拘' in job_year or '無經驗可' in job_year:
            job_year = '0'
            
        else:
            try:
                job_year = re.search(r'\d+',job_year).group()
            except:
                job_year = '0'
    
    #連接資料庫

        db, cursor = DB.db_init()
        if len(conlist) > 0:
            try:
                with db.cursor() as cursor:
                    sql = f'''REPLACE INTO `dream`.`job` (jobtitle,jobcat,joburl,company,city,salary,minsalary,maxsalary,skill,ryear,jd,jr,welfare,source,updatetime) VALUES ("{job_title}","{jobcat}","{url}","{job_company}","{job_city}","{job_salary}",{min},{max},"{job_skill}","{job_year}","{job_description}","{job_other}","{job_welfare}","518人力銀行","{job_date}")'''
                    cursor.execute(sql)
                    db.commit()
            except Exception as e:
                print(e)
                continue
            
            db.close()


if __name__ == '__main__':
    
    with open('jobsearch.txt','r',encoding="utf-8") as f:
        lines = f.readlines()
        words1 = [word.strip() for word in lines]
        
    with open('jobcategory.txt','r',encoding="utf-8") as f:
        lines = f.readlines()
        words2 = [word.strip() for word in lines]
    
    #職缺總數與頁數
    for keyword in words1:
        res = requests.get(f'https://www.518.com.tw/job-index.html?ad={keyword}&al=3')
        
        soup = bs(res.text, 'lxml')
        
        total_count = soup.findAll('span', 'sum')
        if total_count != []:
            total_count = str((total_count)[-1])
            count = re.findall(r'\d+', total_count)[0]
        else:
            count = 0
        
        total_page = soup.findAll('span', 'pagecountnum')
        if total_page != []:
            total_page = str((total_page)[0])
            page = int(re.findall(r'\d+', total_page)[-1])
        else:
            count = 0
            continue
        
        print(keyword, '職缺總數: ', count)
        print(keyword, '職缺頁數: ', page)
        
        find_job_518(keyword)

        f.close()