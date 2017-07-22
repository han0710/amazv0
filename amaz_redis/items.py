# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst

class Product(scrapy.Item):
    prod_code=scrapy.Field()
    prod_title=scrapy.Field()
    prod_descript=scrapy.Field()
    prod_price=scrapy.Field()
    prod_rating=scrapy.Field()
    
class Keyword(scrapy.Item):
    kw_kword=scrapy.Field()
    
class Prod_Kword_Rank(scrapy.Item):
    pk_id=scrapy.Field()
    pkr_rank=scrapy.Field()
    pkr_url=scrapy.Field()
    pkr_qid=scrapy.Field()
    pkr_ip=scrapy.Field()
    pkr_headers=scrapy.Field()

class Store(scrapy.Item):
    market=scrapy.Field()
    merchant=scrapy.Field()
    store_name=scrapy.Field()

class Store_Prod(scrapy.Item):
    store_name=scrapy.Field()
    prod_code=scrapy.Field()
    country=scrapy.Field()