import pymysql
import redis

import amaz_redis.settings as S

SQL_SELECT_KID="SELECT ID FROM KWORD"

def mysql2redis():
	r=redis.StrictRedis(host=S.REDIS_HOST,port=S.REDIS_PORT,password=S.REDIS_PASS)
	
	conn=pymysql.connect(S.MYSQL_HOST,S.MYSQL_USER,S.MYSQL_PASSWORD,S.MYSQL_DB,charset=S.MYSQL_CHARSET)
	cur=conn.cursor()
	cur.execute(SQL_SELECT_KID)
	rets=cur.fetchall()

	for ret in rets:
		kw_id,=ret
		r.lpush('KwRanksSpider:start_kids',kw_id)

if __name__=='__main__':
	mysql2redis()
		
	
	