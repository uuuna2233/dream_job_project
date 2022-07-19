# pip install pymysql

import pymysql

# Connect to the database
class DB:
    def db_init():
        db = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='root',
            port=3306,
            db='dream'
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        return db, cursor

class DB_Table(DB):
    def JobCrawler():
        db, cursor = DB.db_init()
        with db.cursor() as cursor:
            sql = '''
            CREATE TABLE IF NOT EXISTS `dream`.`job`
            (`jobtitle` VARCHAR(200),
             `jobcat` VARCHAR(20),
             `joburl` VARCHAR(200) NOT NULL PRIMARY KEY,
             `company` VARCHAR(200),
             `city` VARCHAR(200),
             `salary` VARCHAR(50),
             `maxsalary` INT(11),
             `minsalary` INT(11),
             `skill` TEXT,
             `ryear` VARCHAR(10),
             `jd` LONGTEXT,
             `jr` LONGTEXT,
             `welfare` LONGTEXT,
             `source` VARCHAR(200),
             `updatetime` DATE,
             `systemtime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON update CURRENT_TIMESTAMP
             )
             '''
            cursor.execute(sql)
            db.commit()
            db.close()
  

DB.db_init()
DB_Table.JobCrawler()
