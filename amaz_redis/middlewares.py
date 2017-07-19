# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from amaz_redis.settings import USER_AGENTS

import random
import pytesseract
import requests
from PIL import Image


class RandomUserAgentMiddleware(object):
	def process_request(self,request,spider):
		request.headers["User-Agent"]=random.choice(USER_AGENTS)

class AmazonCaptchaMiddleware(object):
	def process_response(self,request,response,spider):
		title=response.css("title::text").extract_first()
		if title=="Amazon CAPTCHA":
			img_src=response.css("div['class'='a-row a-text-center'] > img::attr(src)").extract_first()
			self._save_captcha(img_src)
			img=Image.open('captcha.jpg')
			text=pytesseract.img_to_string(img)
				
	def _save_captcha(self,img_src):
		r=requests.get(img_src)
		with open('captcha.jpg','wb') as f:
			f.write(r.content)
		