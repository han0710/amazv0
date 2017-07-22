import pymysql
import amaz_redis.settings as S

CONN=pymysql.connect(S.MYSQL_HOST,S.MYSQL_USER,S.MYSQL_PASSWORD,S.MYSQL_DB,charset=S.MYSQL_CHARSET)
CUR=CONN.cursor()

SQL_SELECT_PKID="SELECT pk.ID FROM PROD_KWORD AS pk \
				 WHERE NOT EXISTS(SELECT * FROM PROD_KWORD_RANK AS pkr \
				 WHERE pk.ID=pkr.PK_ID)"
				 
SQL_SELECT_PK="SELECT p.ASIN,k.KEYWORD FROM \
			   (PROD_KWORD AS pk LEFT JOIN PROD AS p ON pk.PROD_ID=p.ID) \
				LEFT JOIN KWORD AS k ON pk.KWORD_ID=k.ID \
				WHERE pk.ID=%s"
				
def report_unfound_kw_prod():
	CUR.execute(SQL_SELECT_PKID)
	rets=CUR.fetchall()
	
	try:
		with open('unfound_kw_prod.txt','w') as f:
			for ret in rets:
				pkid,=ret
				CUR.execute(SQL_SELECT_PK,pkid)
				asin,kword=CUR.fetchone()
				line='%s\t%s\n'%(asin,kword)
				f.write(line)
	finally:
		f.close()
	
	
		
	
	
	
	