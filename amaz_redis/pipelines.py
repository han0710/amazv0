# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import pymysql


from scrapy.exceptions import DropItem

from amaz_redis.items import Product,Keyword,Prod_Kword_Rank,Store,Store_Prod
import amaz_redis.settings as S

class MySQLPipeline(object):
    def __init__(self):
        self.host=S.MYSQL_HOST
        self.user=S.MYSQL_USER
        self.password=S.MYSQL_PASSWORD
        self.db=S.MYSQL_DB
        self.charset=S.MYSQL_CHARSET
    
        self.PKR_INSERT_PKR="INSERT IGNORE INTO PROD_KWORD_RANK (PK_ID,RANK,URL,QID,HEADERS) VALUES (%s,%s,%s,%s,%s);"
        self.P_INSERT_ASIN_COUNTRY="INSERT IGNORE INTO PROD (ASIN,COUNTRY) VALUES (%s,%s);"
        self.S_INSERT_NAME="INSERT IGNORE INTO STORE (NAME) VALUES (%s);"
        self.SP_INSERT_ID="INSERT IGNORE INTO STORE_PROD (STORE_ID,PROD_ID) \
                            SELECT s.ID,p.ID FROM STORE AS s, PROD AS p \
                            WHERE s.NAME=%s AND p.ASIN=%s;"
        
    def open_spider(self,spider):
        self.connection=pymysql.connect(self.host,self.user,self.password,self.db,charset=self.charset)
        self.cursor=self.connection.cursor()
        
    def close_spider(self,spider):
        self.connection.close()
        
    def process_item(self,item,spider):
        if isinstance(item,Prod_Kword_Rank):
            item=dict(item)
            pkid=item['pk_id'][0]
            rank=item['pkr_rank'][0]
            url=item['pkr_url'][0]
            qid=item['pkr_qid'][0]
            headers=item['pkr_headers'][0]
            self.cursor.execute(self.PKR_INSERT_PKR,(pkid,rank,url,qid,headers))
            self.connection.commit()
            print('产品-关键字-排名已存入')
        elif isinstance(item,Store):
            item=dict(item)
            name=item['store_name'][0]
            self.cursor.execute(self.S_INSERT_NAME,name)
            self.connection.commit()
            print('店铺已存入')
        elif isinstance(item,Store_Prod):
            item=dict(item)
            store_name=item['store_name'][0]
            prod_asin=item['prod_code'][0]
            country=item['country'][0]
            self.cursor.execute(self.P_INSERT_ASIN_COUNTRY,(prod_asin,country))
            self.cursor.execute(self.SP_INSERT_ID,(store_name,prod_asin))
            self.connection.commit()
            print('产品及店铺-产品已存入')
        else:
            raise DropItem('%s'%item)
        return item
        
