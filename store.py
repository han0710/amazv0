import redis

import amaz_redis.settings as S

def insert_data_store():
	r=redis.StrictRedis(host=S.REDIS_HOST,port=S.REDIS_PORT,password=S.REDIS_PASS)
	r.delete('amaz_stores:start_urls','amaz_stores:dupefilter')
	r.lpush('amaz_stores:start_urls','https://www.amazon.com/s?marketplaceID=ATVPDKIKX0DER&me=A3NSAWXK9GGIBU&merchant=A3NSAWXK9GGIBU&redirect=true',
			'https://www.amazon.com/s?marketplaceID=ATVPDKIKX0DER&me=A1VJ2S43J79NA1&merchant=A1VJ2S43J79NA1&redirect=true',
			'https://www.amazon.com/s?marketplaceID=ATVPDKIKX0DER&me=A3088WJRGH940N&merchant=A3088WJRGH940N&redirect=true')
			
if __name__=='__main__':
	insert_data_store()