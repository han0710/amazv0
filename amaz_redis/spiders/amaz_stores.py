# -*- coding: utf-8 -*-
import scrapy
import pymysql
import re

from scrapy.loader import ItemLoader
from scrapy_redis.spiders import RedisSpider
from scrapy.shell import inspect_response

import amaz_redis.settings as S
from amaz_redis.items import Store,Store_Prod

class AmazStoresSpider(RedisSpider):
    name = 'amaz_stores'
    redis_key='amaz_stores:start_urls'
    
    def __init__(self,*args,**kwargs):
        self.allowed_domains=[]
        for i in S.REGIONS.values():
            self.allowed_domains.append(i)
        super(AmazStoresSpider,self).__init__(*args,**kwargs)
        
        self.HEADERS={S.REGIONS['JP']:{"Host":"www.amazon.co.jp",
                                       "Referer":"https://www.amazon.co.jp/"
                                        },
                      S.REGIONS['GB']:{"Host":"www.amazon.com",
                                       "Referer":"https://www.amazon.com/"},
        } 
        
        self.CSS_STOREFRONT="span[class='a-color-state a-text-bold']::text"
        self.CSS_PAGE_NUM="div#pagn > span:nth-last-child(3) > a::text"
        self.CSS_LIS="li[id^='result']::attr(data-asin)"
        self.RE_COUNTRY=".*www\.(.*)/.*"
        self.RE_NAME="(.*) Storefront"
        
        self.CONN=pymysql.connect(S.MYSQL_HOST,S.MYSQL_USER,S.MYSQL_PASSWORD,S.MYSQL_DB,charset=S.MYSQL_CHARSET)
        self.CUR=self.CONN.cursor()
    
    def make_request_from_data(self,data):
        url=data.decode()
        country=re.match(self.RE_COUNTRY,url).group(1)
        headers=self.HEADERS[country]
        return scrapy.Request(url=url,callback=self.parse,headers=headers)
        
    def parse(self, response):
        storefront=response.css(self.CSS_STOREFRONT).extract_first()
        name=re.match(self.RE_NAME,storefront).group(1)
        
        store_loader=ItemLoader(item=Store())
        store_loader.add_value('store_name',name)
        yield store_loader.load_item()
        
        #inspect_response(response,self)
        page_num=response.css(self.CSS_PAGE_NUM).extract_first()
        # 如果分页
        if page_num:
            for i in range(int(page_num)):
                url='%s&page=%s'%(response.url,i+1)
                yield scrapy.Request(url=url,callback=self.page_parse,meta={'name':name})
        else:
            return self.page_parse(response)
        
    def page_parse(self,response):
        lis=response.css(self.CSS_LIS).extract()
        for li in lis:            
            store_prod_loader=ItemLoader(item=Store_Prod())
            store_prod_loader.add_value('store_name',response.meta['name'])
            store_prod_loader.add_value('prod_code',li)
            yield store_prod_loader.load_item()
        
