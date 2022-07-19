''' 此為定期更新版本(更新頻率: 暫定每 2 天更新)，若為第一次蒐集「全部」資料進資料庫，將 get url 參數改為 'da=30' 即可 '''

from fake_useragent import UserAgent
import time
import random
import requests
from urllib.parse import quote
from lxml import html
import re
import pandas as pd
from sqlalchemy import create_engine
from fuzzywuzzy import process
from bs4 import BeautifulSoup as bs
import requests.packages.urllib3
from Salary_clear import SalaryClear
requests.packages.urllib3.disable_warnings()   # Fix InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised.

connect_info = 'mysql+pymysql://root:root@localhost:3306/dream?charset=utf8'
engine = create_engine(connect_info)

def jobCategory(keyword):
    """判斷職務類別"""     
    with open(r'jobcategory.txt','r',encoding="utf-8") as f:
        lines = f.readlines()
        words2 = [word.strip() for word in lines]

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

def requirements(jd, jq, skill):
    """判斷技能要求是否與所學相關"""
    pattern = r'IoT|Linux|Python|MySQL|SQL|API|Hadoop|InfluxDB|ELK|Elastic Search|Logstash|Kibana|Splunk|AWS|Tableau|Qlik|PowerBI|BI​|GCP|Oracle Data Visualization|Big Data|Machine Learning|TensorFlow|Deep Learning|Crawler|Data Collection|Data Modeling|Data Mining|Data Cleaning|Data Visualization|Data Pipeline|Flask|Hive|sqoop|impala|flume|oozie|MongoDB|ETL|ELT|Git|Azure|Algorithm|大數據|資料收集|數據收集|資料建模|數據建模|資料清洗|數據清洗|資料清理|數據清理|視覺化|爬蟲|機器學習|深度學習|資料工程|資料探勘|演算法'
    jobRequired = str([jd] + [jq] + [skill])
    skills = re.findall(pattern, jobRequired, flags=re.I)
    conformity = set(sk.casefold() for sk in skills)
    conlist=list(conformity)
    constr="/".join(co.replace('\u200b','').replace('mysql', 'sql').replace('powerbi', 'bi').replace('大數據', 'big data').replace('機器學習', 'machine learning').replace('深度學習', 'deep learning').replace('資料收集', 'data collection').replace('數據收集', 'data collection').replace('資料建模', 'data Modeling').replace('數據建模', 'ata Modeling').replace('資料清洗', 'data cleaning').replace('數據清洗', 'data cleaning').replace('資料清理', 'data cleaning').replace('數據清理', 'data cleaning').replace('視覺化', 'data visualization').replace('爬蟲', 'crawler').replace('資料探勘', 'data mining').replace('演算法', 'algorithm') for co in conlist)

    return constr


def get_job_1111(url):
    """搜尋職缺詳情"""
    s = requests.get(url)
    joburl_content=re.compile(r'<div class="job_item_info">.*?<a href="(?P<url>.*?)" target="_blank"><h5 class="card-title title_6">',re.S)
    joburl=joburl_content.findall(s.text)

    with open(r'jobcategory.txt','r',encoding="utf-8") as f:
            lines = f.readlines()
            words2 = [word.strip() for word in lines]   
            
    for i in list(set(joburl)):

        ua=UserAgent()
        headers = {'user-agent': ua.random}
        s=requests.Session()
        req=s.get(i, headers=headers,verify=False)
        resp=req.text
        tree=html.fromstring(req.text)
        
        name1=tree.xpath("//h1[@class='title_4']")
        name=name1[0].text if name1 != [] else 'Null'

        if process.extractOne(name, words2)[1] > 50:                                 
            jobcat=jobCategory(process.extractOne(name, words2)[0])       
        else:
            jobcat=jobCategory(key_txt.strip())
   
        company1=tree.xpath("//a[@class='ui_card_company_link']/span[@class='title_7']")
        company=company1[0].text if company1 != [] else 'Null'
        
        city1=tree.xpath("//div/span/u")
        city=city1[0].text[:4] if city1  != [] else 'Null'


        salary_content=re.compile(r'<div class="ui_items job_salary">.*?<p class="body_2">(?P<salary>.*?)</p>',re.S)
        salary=salary_content.findall(resp)
        salary="".join(salary)
        nnsa=[float(s.replace(',', '')) for s in re.findall(r'-?\d+\.?\,?\d*',salary)]
        
        max50, min50 = SalaryClear.newsalary(jobcat)
        
        try:
            if len(nnsa)==2:
                if "月薪" in salary or "時薪" in salary or "日薪" in salary:  
                    minsa=float(nnsa[0])
                    maxsa=float(nnsa[1])
                    if "萬" in salary:
                        minsa=minsa*10000
                        maxsa=maxsa*10000
                elif "年薪" in salary:
                    minsa=float(nnsa[0])/12
                    maxsa=float(nnsa[1])/12          
                    if "萬" in salary:
                        minsa=minsa*10000
                        maxsa=maxsa*10000
                else:
                    minsa=maxsa='null'
                    
            elif len(nnsa)==1:
                if "面議" in salary:
                    minsa=40000
                    maxsa=max50
                elif "月薪" in salary or "時薪" in salary or "日薪" in salary:
                    minsa=maxsa=float(nnsa[0])
                    if "以上" in salary and "萬" in salary:
                        minsa=minsa*10000
                        maxsa=max50
                    elif "萬" in salary:
                        minsa=maxsa=minsa*10000
                    elif "以上" in salary:
                        maxsa=max50
        
                elif "年薪" in salary:
                    minsa=maxsa=float(nnsa[0])/12
                    if "以上" in salary and "萬" in salary:
                        minsa=minsa*10000
                        maxsa=max50
                    elif "萬" in salary:
                        minsa=maxsa=minsa*10000
                    elif "以上" in salary:
                        maxsa=max50
        
                else:
                    minsa=maxsa='null'
            else:
                minsa=maxsa='null'
        except Exception as e:
            print(e)
            minsa=maxsa='null'
            continue

        jobdp_content=re.compile(r'<div class="content_items job_description">.*?<h6 class="title_6 title spy_item" id="jobs_content">工作內容</h6>.*?<div class="body_2 description_info">(?P<jd>.*?)</div>',re.S)
        jobdp=jobdp_content.findall(resp)
        jd=("".join(jobdp)).replace("&nbsp;","").replace("</p>","").replace("<p>","").replace("\n","").replace("\r","").replace("</br>;","").replace("<br>;","")

        jobdr_content=re.compile(r'<div class="d-flex m_info_group conditions">.*?<div class="job_info_title">附加條件：</div>.*?<div class="job_info_content">.*?<div class="ui_items_group">(?P<jr>.*?)</div>',re.S)
        jobdr=jobdr_content.findall(resp)
        jr=("".join(jobdr)).replace("&nbsp;","").replace("</p>;","").replace("<p>;","").replace("\n","").replace("\r","")

        if tree.xpath("//a[@class='btn_secondary_5 btn_size_5 mr-2 mb-2']") != []:
            for skilll in tree.xpath("//a[@class='btn_secondary_5 btn_size_5 mr-2 mb-2']"):
                try:
                    global skill
                    skill=skilll.text.strip()
                except Exception as e:
                    print(e)
                    continue
        else:
            skill='Null'

        updatetime1=tree.cssselect("body > div.job_detail_view2 > div.job_detail_wrapper > div.job_detail_region > div > div > div.ui_job_detail > div:nth-child(3) > small")
        updatetime=updatetime1[0].text[3:] if updatetime1 != [] else 'Null'
        constr = requirements(jd, jr, skill)

        try:
            dit={
                "jobtitle":name,
                "jobcat":jobcat,
                "joburl":i,
                "company":company,
                "city":city,
                "salary":salary,
                "minsalary":minsa,
                "maxsalary":maxsa,
                "skill":constr,
                "ryear":None,
                "jd":jd,
                "jr":jr,
                "welfare":None,
                "source":'1111人力銀行',
                "updatetime":updatetime
                }

            jobdata = pd.DataFrame(dit,index=[0])
            
        except Exception as e:
                print(e) 
                continue
        
        time.sleep(random.uniform(0, 1))
        s.close()
    
        
        if requirements(jd, jr, skill) != '':
            try:
                pd.io.sql.to_sql(jobdata, "job", con=engine, index=False, if_exists='append')                     
            except:
                time.sleep(500)
                continue
  

def find_title_1111(key_txt):
    """職缺總數和頁數"""
    key = quote(key_txt)
    url = f'https://www.1111.com.tw/search/job?da=3&ks={key}'
    res= requests.get(url)
    soup = bs(res.text, 'lxml')
    data = soup.findAll('div','srh-result-count nav_item job_count')
    # print(data) # [<div aria-label="筆資料" class="srh-result-count nav_item job_count" data-condition="1" data-count="213"></div>]

    # replace: Fix ValueError: invalid literal for int() with base 10: '2,493'
    job_count = int((re.findall(r'\d+[,]*\d*',str(data[0]).split(' ')[-1].split('><')[0])[0]).replace(',',''))
    print(key_txt, '職缺總數: ', job_count)
    page_count = job_count//20 + 1
    for i in range(page_count):
        find_page_url = 'https://www.1111.com.tw/search/job?da=3&ks={0}&page={1}'.format(key,i)
        get_job_1111(find_page_url)
        if i == 100:
            break
        

if __name__ == '__main__':

    f = open(r'jobsearch.txt',"r",encoding="utf-8")
    for key_txt in f.readlines():
        find_title_1111(key_txt.strip())

    f.close()