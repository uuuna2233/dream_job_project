import re
import requests
from lxml import html
import pymysql
from fuzzywuzzy import process
from fake_useragent import UserAgent
from Salary_clear import SalaryClear


conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="root", database="dream")
cursor = conn.cursor()


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


def find_job_yourator(q):
    """取得職缺詳情""" 
    ua=UserAgent()
    headers = {'user-agent': ua.random}
    url=[]
    for i in range(1,20):
        resp=requests.get(f'https://www.yourator.co/api/v2/jobs?term[]={q}&sort=recent_updated&page={i}',headers=headers)
        content=resp.json()

        pathurl='https://www.yourator.co'
        for i in content['jobs']:
            jurl=pathurl+i['path']#分頁網址
            url.append(jurl)


    with open(r'jobcategory.txt','r',encoding="utf-8") as f:
        lines = f.readlines()
        words2 = [word.strip() for word in lines]
        
    for i in list(set(url)):
        res=requests.get(i,headers=headers)
        tree=html.fromstring(res.text)
        for name in tree.xpath("//section/div/div/div/div/h1"):
            jname=name.text
        for com in tree.xpath("//h4/a"):
            company=com.text
        for local in tree.xpath("//div[2]/p/a"):
            city=local.text[3:]
        for update in tree.xpath("//p[@class='basic-info__last_updated_at']"):
            uptime=update.text[6:]


        resp=res.text
        jb_content=re.compile(r'<h2 class="job-heading">工作內容</h2>.*?<section class="content__area">.*?<p>(?P<jb>.*?)</p>',re.S)
        jb=jb_content.findall(resp)
        jbb="".join(jb).replace("<br>","").replace("</br>","").replace("<strong>","").replace("</strong>","").replace("<b>","").replace("</b>","")
        jdd=re.findall(r'\S+',jbb)
        jd="".join(jdd)


        jr_content=re.compile(r'<h2 class="job-heading">條件要求</h2>.*?<section class="content__area">.*?<p>(?P<jr>.*?)</section>',re.S)
        jrequest=jr_content.findall(resp)
        jrrr="".join(jrequest).replace("<br>","").replace("</br>","").replace("<strong>","").replace("</strong>","").replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","").replace("<ul>","").replace("</ul>","").replace("<li>","").replace("</li>","")
        jrr=re.findall(r'\S+',jrrr)
        jr="".join(jrr)


        wfff=jr_content.findall(resp)
        wel="".join(wfff).replace("<br>","").replace("</br>","").replace("<strong>","").replace("</strong>","").replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","").replace("<ul>","").replace("</ul>","").replace("<li>","").replace("</li>","")
        wff=re.findall(r'\S+',wel)
        wf="".join(wff)

        sa_content=re.compile(r'<h2 class="job-heading">薪資範圍</h2>.*?<section class="content__area">(?P<sa>.*?)</section>',re.S)
        ssa=sa_content.findall(resp)
        sa="".join(ssa)

        
        nsa="".join(sa).replace(",","") # 轉字串+拿掉，
        nnsa=re.findall(r'\d+',nsa) # 取數字(會變list)

        skill_content=re.compile(r'<a class="tag" href=.*?">(?P<skill>.*?)</a>',re.S)
        skilll=skill_content.findall(resp)
        skill="/".join(skilll)
        
    
        if requirements(jd, jr, skill) != '':
            if process.extractOne(jname, words2)[1] > 50:                             
                jobcat=jobCategory(process.extractOne(jname, words2)[0])       
            else:
                jobcat=jobCategory(q)
            
            max50, min50 = SalaryClear.newsalary(jobcat)
            try:
                if len(nnsa)==2:
                    if "月薪" in sa:
                        minsa=nnsa[0]
                        maxsa=nnsa[1]
                    if "時薪" in sa:
                        minsa=nnsa[0]
                        maxsa=nnsa[1]
                    elif "年薪" in sa:
                        minsa=float(nnsa[0])/12
                        maxsa=float(nnsa[1])/12
                elif len(nnsa)==1:
                    if "面議" in sa:
                        minsa=40000
                        maxsa=max50
                    elif "時薪" in sa:
                        minsa=nnsa[0]
                        maxsa=nnsa[0]
                    elif "月薪" in sa:
                        minsa=nnsa[0]
                        maxsa=max50
                    elif "年薪" in sa:
                        minsa=float(nnsa[0])/12
                        maxsa=max50
                else:
                    minsa=maxsa='null'
            except Exception as e:
                    print(e)
                    continue

            # 連接資料庫
            try:
                sql= f'''REPLACE INTO `dream`.`job`
                        (jobtitle,jobcat,joburl,company,city,salary,maxsalary,minsalary,skill,jd,jr,welfare,source,updatetime) VALUES
                        ("{jname}","{jobcat}","{i}","{company}","{city}","{sa}",{maxsa},{minsa},"{requirements(jd, jr, skill)}","{jd}","{jr}","{wf}","yourator","{uptime}")'''
                # print(sql)
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(e)
                continue
            
            res.close()
            conn.close()


if __name__ == '__main__':
    
    with open(r'jobsearch.txt','r',encoding="utf-8") as f:
        for line in f.readlines():
            find_job_yourator(line.strip())    
           
    
   
    