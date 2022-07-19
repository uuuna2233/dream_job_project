''' 此為定期更新版本(更新頻率: 暫定 3 天一次)，若為第一次蒐集「全部」資料進資料庫，將 for 迴圈頁數改為 45，183行 d.day 改為 <=30 即可 '''

import requests
import re
from bs4 import BeautifulSoup as bs
import time
import datetime
from fuzzywuzzy import process
from fake_useragent import UserAgent
from DB_initial import DB

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


def requirements(jd, jq, skill):
    """判斷技能要求是否與所學相關"""
    pattern = r'IoT|Linux|Python|MySQL|SQL|API|Hadoop|InfluxDB|ELK|Elastic Search|Logstash|Kibana|Splunk|AWS|Tableau|Qlik|PowerBI|BI​|GCP|Oracle Data Visualization|Big Data|Machine Learning|TensorFlow|Deep Learning|Crawler|Data Collection|Data Modeling|Data Mining|Data Cleaning|Data Visualization|Data Pipeline|Flask|Hive|sqoop|impala|flume|oozie|MongoDB|ETL|ELT|Git|Azure|Algorithm|大數據|資料收集|數據收集|資料建模|數據建模|資料清洗|數據清洗|資料清理|數據清理|視覺化|爬蟲|機器學習|深度學習|資料工程|資料探勘|演算法'
    jobRequired = str([jd] + [jq] + [skill])
    skills = re.findall(pattern, jobRequired, flags=re.I)
    
    # 合併同義詞
    skills=[Sk.replace('mysql', 'sql').replace('powerbi', 'bi').replace('大數據', 'big data').replace('機器學習', 'machine learning').replace('深度學習', 'deep learning').replace('資料收集', 'data collection').replace('數據收集', 'data collection').replace('資料建模', 'data Modeling').replace('數據建模', 'ata Modeling').replace('資料清洗', 'data cleaning').replace('數據清洗', 'data cleaning').replace('資料清理', 'data cleaning').replace('數據清理', 'data cleaning').replace('視覺化', 'data visualization').replace('爬蟲', 'crawler').replace('資料探勘', 'data mining').replace('演算法', 'algorithm') for Sk in skills]

    conformity = set(sk.casefold() for sk in skills)
    conlist=list(conformity)
    constr="/".join(conlist)
    return constr


def find_job_cakeresume(q):
    """取得職缺詳情"""     
    ua=UserAgent()
    headers = {'user-agent': ua.random}
    jurl=[]
    for i in range(1,30):
        url=requests.get(f'https://www.cakeresume.com/jobs?q={q}&&refinementList%5Border%5D=latest&page={i}',headers=headers)
        soup = bs(url.text, 'html.parser')
        for link in soup.find_all("a", "job-link"):  # 公司網址
            l = link.get('href')
            jurl.append(l)
            

    for i in list(set(jurl)):
        url=requests.get(i,headers=headers)
        url_content=url.text

        name_content=re.compile(r'<h2 class="JobDescriptionLeftColumn_title__heKvX">(?P<jname>.*?)</h2>',re.S)
        name=name_content.findall(url_content)
        jname="".join(name)
            
        if process.extractOne(jname, words2)[1] > 50:                                 
            jobcat=jobCategory(process.extractOne(jname, words2)[0])       
        else:
            jobcat=jobCategory(q)

        
        company_content=re.compile(r'<div class="JobDescriptionLeftColumn_companyInfo__WRlaG">.*?<a href=".*?" target="_blank" rel="noreferrer" class="JobDescriptionLeftColumn_name__ORyQt">(?P<company>.*?)</a>',re.S)
        com=company_content.findall(url_content)
        company="".join(com)

        jb_content=re.compile(r'<h3 class="ContentSection_title__Ox8_s">Job Description</h3>.*?<div class="RailsHtml_container__VVQ7u">.*?<p>(?P<jd>.*?)</div>',re.S)
        jb=jb_content.findall(url_content)
        jd=("".join(jb)).replace('</p>\r\n<p>',"").replace('<p>',"").replace('</p>',"").replace('<br />',"").replace('<li>',"").replace('</li>',"").replace('</ol>',"").replace('<ol>',"").replace('<ul>',"").replace('</ul>',"").replace('"',"'")

        jreq_content=re.compile(r'<h3 class="ContentSection_title__Ox8_s">Requirements</h3>.*?<div class="RailsHtml_container__VVQ7u">.*?<p>(?P<jr>.*?)</div>',re.S)
        jreq=jreq_content.findall(url_content)
        jq="".join(jreq).replace('</p>\r\n<p>',"").replace('<p>',"").replace('</p>',"").replace('<br />',"").replace('<li>',"").replace('</li>',"").replace('</ol>',"").replace('<ol>',"").replace('<ul>',"").replace('</ul>',"").replace('"',"'")

        local_content=re.compile(r'<div class="Tooltip_wrapper__Aw9UF">.*?<div class="Tooltip_handle__PbVuc">.*?<a href=".*?" target="_blank" rel="noreferrer">(?P<city>.*?)</a>.*?<div class="Avatar_wrapper__IuVWG" style="height:44px;width:44px">',re.S)
        local=local_content.findall(url_content)
        city="".join(local).replace("Taipei City","台北市").replace("New Taipei City","新北市").replace("Taipei","台北市").replace("台灣台北","台北市").replace("New ","")
        if city == '' or len(city) > 200:
            try:
                local_content=re.compile(r'class="CompanyInfoItem_link__E841d">(.*?)</a>',re.S)
                local=local_content.findall(url_content)
                city=re.findall(r'\D+\S*',local[0])[0].strip()
            except:
                city='Null'

        salary_content=re.compile(r'<div class="JobDescriptionRightColumn_salaryWrapper__mYzNx"(?P<salary>.*?)</div>',re.S)
        sa=salary_content.findall(url_content)
        salary="".join(sa)
        nnsa=[float(s) for s in re.findall(r'-?\d+\.?\d*',salary)]
        try:
            if len(nnsa)==2:
                if "month" in salary:
                    if "K" in salary and "M" in salary:
                        minsa=nnsa[0]*1000
                        maxsa=nnsa[1]*1000000
                    elif "K" in salary:
                        minsa=nnsa[0]*1000
                        maxsa=nnsa[1]*1000
                    elif "M" in salary:
                        minsa=nnsa[0]*1000000
                        maxsa=nnsa[1]*1000000

                elif "year" in salary:
                    if "K" in salary and "M" in salary:
                        min=float(nnsa[0]*1000)
                        max=float(nnsa[1]*1000000)
                        minsa=min/12
                        maxsa=max/12
                    elif "M" in salary:
                        min=float(nnsa[0]*1000000)
                        max=float(nnsa[1]*1000000)
                        minsa=min/12
                        maxsa=max/12
                    elif "K" in salary:
                        min=float(nnsa[0]*1000)
                        max=float(nnsa[1]*1000)
                        minsa=min/12
                        maxsa=max/12
                else:
                    minsa=0
                    maxsa=0
        except Exception as e:
                print(e)
                continue

        tag_content=re.compile(r'<a href=".*?" class="Tags_item__YXJjk Tags_itemClickable__fIctK">(?P<skill>.*?)</a>.*?</div>',re.S)
        tag=tag_content.findall(url_content)
        skill="/".join(tag)

        update_time=re.compile(r'"content_updated_at":"(\d+-\d+-\d+).*?"',re.S)
        update=update_time.search(url_content).group(1)
        d1=datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
        d2=datetime.datetime.strptime(str(update), '%Y-%m-%d')
        d=d1-d2  

        time.sleep(1)
        url.close()


    # 連接資料庫
    # 所需技能不為空且更新日小於30天才進資料庫
        db, cursor = DB.db_init()
        if requirements(jd, jq, skill) != '' and d.days <=3:
            try:
                with db.cursor() as cursor:
                    sql= f'''REPLACE INTO `dream`.`job` (jobtitle,jobcat,joburl,company,city,salary,minsalary,maxsalary,skill,jd,jr,source,updatetime) VALUES ("{jname}","{jobcat}","{i}","{company}","{city}","{salary}",{minsa},{maxsa},"{requirements(jd, jq, skill)}","{jd}","{jq}","cakeresume","{update}")'''
                    cursor.execute(sql)
                    db.commit()
            except Exception as e:
                    print(jname, i)
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
    
    for keyword in words1:
        find_job_cakeresume(keyword)
        print(keyword, '職缺已匯入')

    f.close()