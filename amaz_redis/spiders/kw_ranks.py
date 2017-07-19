# -*- coding: utf-8 -*-
import scrapy
import re
import json
import pymysql

from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from scrapy_redis.spiders import RedisSpider

from amaz_redis.items import Prod_Kword_Rank
import amaz_redis.settings as S

from scrapy.shell import inspect_response

class KwRanksSpider(RedisSpider):
    name = 'kw_ranks'
    redis_key='kw_ranks:start_kids'
    
    def __init__(self,*args,**kwargs):
        self.allowed_domains=[]
        for i in S.REGIONS.values():
            self.allowed_domains.append(i)
        super(KwRanksSpider,self).__init__(*args,**kwargs)
        
        self.URL_PROD_KWORD={S.REGIONS['GB']:"https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias=aps&field-keywords=%s",
                            S.REGIONS['JP']:"https://www.amazon.co.jp/s/ref=nb_sb_noss?__mk_ja_JP=カタカナ&url=search-alias=aps&field-keywords=%s"}
        self.HEADERS={S.REGIONS['JP']:{"Host":"www.amazon.co.jp",
                                       "Referer":"https://www.amazon.co.jp/"
                                        },
                      S.REGIONS['GB']:{"Host":"www.amazon.com",
                                       "Referer":"https://www.amazon.com/"},
        }  
        
        self.SQL_SELECT_KW="SELECT KEYWORD FROM KWORD WHERE ID=%s"
        self.SQL_SELECT_PKID_ASIN_COUNTRY='''
                                    SELECT pk.ID,p.ASIN,p.COUNTRY FROM PROD_KWORD AS pk LEFT JOIN PROD AS p ON pk.PROD_ID=p.ID
                                    WHERE pk.KWORD_ID=%s
                                '''
        self.CSS_LIS="li[id^=result]"
        self.CSS_SPONSOR="h5"
        self.CSS_PROD_ID="::attr('data-asin')"
        self.CSS_PROD_URL="a[class='a-link-normal a-text-normal']::attr(href)"
        self.CSS_NEXT_PAGE="a.pageNext::attr(href)"
        self.RE_PROD_URL=r"(.*)/ref=sr_1_([0-9]{1,})(.*)qid=([0-9]{1,})&sr(.*)"
        
        self.CONN=pymysql.connect(S.MYSQL_HOST,S.MYSQL_USER,S.MYSQL_PASSWORD,S.MYSQL_DB,charset=S.MYSQL_CHARSET)
        self.CUR=self.CONN.cursor()
        
    # 重写scrapy-redis中的函数
    def make_request_from_data(self,data):
        kid = int(data.decode())
        self.CUR.execute(self.SQL_SELECT_PKID_ASIN_COUNTRY,kid)
        rets=self.CUR.fetchall()
        
        if rets is None:
            raise CloseSpider('该关键字没有对应的产品!')
        else:
            prods=[]
            pkids={}
            for ret in rets:
                pk_id,prod,country=ret
                prods.append(prod)
                pkids[prod]=pk_id
            
            self.CUR.execute(self.SQL_SELECT_KW,kid)
            kword,=self.CUR.fetchone()
            words=kword.split()
            k='+'.join(words)
            
            url=self.URL_PROD_KWORD[country]%k
            headers=self.HEADERS[country]
            meta={'prods':prods,'pkids':pkids}
            return scrapy.Request(url=url,callback=self.parse,headers=headers,meta=meta)
        
    def parse(self, response):
        asins_not_found=True
        
        lis=response.css(self.CSS_LIS)
        #print(response.meta['prods'])
        
        for li in lis:
            # 注意到sponsor产品的sponsor标签放在h5标签中，据此加以排除
            sponsor=li.css(self.CSS_SPONSOR)
            if not sponsor:
                prod_id=li.css(self.CSS_PROD_ID).extract_first()
                if prod_id in response.meta['prods']:
                    print('####################')
                    response.meta['prods'].remove(prod_id)
                    prod_url=li.css(self.CSS_PROD_URL).extract_first()
                    rank,qid=self._prod_url_parser(prod_url)
                    headers=response.request.headers
                    res={}
                    for k in headers.keys():
                        res[k.decode()]=headers[k].decode()
                    
                    pkr_loader=ItemLoader(item=Prod_Kword_Rank())
                    pkr_loader.add_value('pk_id',response.meta['pkids'][prod_id])
                    pkr_loader.add_value('pkr_rank',rank)
                    pkr_loader.add_value('pkr_qid',qid)
                    pkr_loader.add_value('pkr_url',prod_url)
                    pkr_loader.add_value('pkr_headers',json.dumps(res))
                    yield pkr_loader.load_item()
        
        asins_not_found=False if not response.meta['prods'] else True
        
        inspect_response(response,self)
        
        if asins_not_found:
            next_page=response.css(self.CSS_NEXT_PAGE).extract_first()
            url=response.urljoin(next_page)
            headers=response.request.headers
            print('new request:%s'%url)
            yield scrapy.Request(url=url,callback=self.parse,headers=headers,meta=response.meta)
        
    def _prod_url_parser(self,prod_url):
        ret=re.match(self.RE_PROD_URL,prod_url)
        rank=int(ret.group(2))
        qid=int(ret.group(4))
        return rank,qid
