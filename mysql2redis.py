import pymysql
import redis
from scrapy_redis.connection import get_redis_from_settings

import amaz_redis.settings as S

URL_PROD_KWORD={S.REGIONS['GB']:"https://www.amazon.com/s/ref=nb_sb_noss2?url=search-alias=aps&field-keywords=%s",
                            S.REGIONS['JP']:"https://www.amazon.co.jp/s/ref=nb_sb_noss2?__mk_ja_JP=カタカナ&url=search-alias=aps&field-keywords=%s"}
SQL_SELECT_KID="SELECT ID FROM KWORD"

def mysql2redis():
	r=get_redis_from_settings(S)
	
	conn=pymysql.connect(S.MYSQL_HOST,S.MYSQL_USER,S.MYSQL_PASSWORD,S.MYSQL_DB,charset=S.MYSQL_CHARSET)
	cur=conn.cursor()
	cur.execute(SQL_SELECT_KID)
	rets=cur.fetchall()

	for ret in rets:
		kw_id,=ret
		r.lpush('KwRanksSpider:start_kids',kw_id)

if __name__=='__main__':
	mysql2redis()
		
	
	