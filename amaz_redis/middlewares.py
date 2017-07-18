# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from amaz_redis.settings import USER_AGENTS
import random

class RandomUserAgentMiddleware(object):
	def process_request(self,request,spider):
		request.headers["User-Agent"]=random.choice(USER_AGENTS)