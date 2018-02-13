# -*- coding: utf-8 -*-

"""
RSS Class for grabbing, formatting and outputing information from streams

Note - Only 6 feeds can be scrapped at a time
Note - added # -*- coding: utf-8 -*- due to entries using that encoding
"""

import time
import os
import logging
import re
from html.parser import HTMLParser
import feedparser


class MLStripper(HTMLParser):
	def __init__(self):
		self.reset()
		self.strict = False
		self.convert_charrefs = True
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)

def strip_tags(html):
	"""
	Strip out HTML from text
	"""
	s = MLStripper()
	try:
		s.feed(html)
		return s.get_data()
	except Exception as err:
		MAIN_LOGGER.error('Stripping HTML failed: %s', err)
		return html

class RSS:
	"""
	RSS Class
	"""
	def __init__(self, rssurl):
		"""
		Constructor method
		"""
		# rss feed url
		self.rss_url = rssurl

		# six randomly selected urls
		self.rssurls_rand = []

		# will hold news item entries
		self.news_entries = []

		self.feeds = [] # will hold current rss feed data

		# class logging setup
		self.loggingDIR = '{}/logs/'.format(
			os.path.dirname(os.path.realpath(__file__)))

		self.logger = logging.getLogger('newsirc.RSS')
		logFileHandler = logging.FileHandler(
			time.strftime(
				"{}RSS%m%d%Y.log".format(self.loggingDIR))
		)
		logFormat = logging.Formatter(
			"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		logFileHandler.setFormatter(logFormat)
		self.logger.addHandler(logFileHandler)

	def getNews(self, url=None):
		"""
		Used as a worker - grabs information from news rss links
		via feedparser
		"""

		print("getNews URL: {}".format(url))

		try:
			fpobj = feedparser.parse(url)
			print('entries: {}'.format(len(fpobj)))
			self.news_entries = fpobj['entries']
		except Exception as err:
			self.logger.error('Feedparsing failed: %s', err)


	def readFeed(self):
		"""
		Get RSS feed information
		"""
		self.getNews(self.rss_url)

	def printArticle(self):
		if self.news_entries:
			self.logger.info('Sending single article')
			entry = self.news_entries[0]
			try:
				newsDesc = strip_tags(entry['description']).strip()

				# if description has multiple breaks don't show it
				if len(newsDesc.split('\n')) > 1:
					newsLineOne = "\002{}".format(entry['title'].strip())
					newsLineTwo = None
					newsLineThree = "\037{}".format(entry['link'].strip())
				# check to see if description is empty or not
				elif bool(re.sub(r"\s+", "", newsDesc, flags=re.UNICODE)):
					newsLineOne = "\002{}".format(entry['title'].strip())
					newsLineTwo = "\035{}".format(newsDesc)
					newsLineThree = "\037{}".format(entry['link'].strip())
				else:
					newsLineOne = "\002{}".format(entry['title'].strip())
					newsLineTwo = None
					newsLineThree = "\037{}".format(entry['link'].strip())

				if newsLineTwo:
					newsline = [
						newsLineOne,
						newsLineTwo,
						newsLineThree
					]
				else:
					newsline = [
						newsLineOne,
						newsLineThree
					]
				self.logger.info('Sending %s\n\n', newsline)

				return newsline
			except KeyError as err:
				self.logger.error('KeyError with entry %s - %s', entry, err)
		else:
			self.logger.info('Article list is empty - refeeding')
			self.readFeed()
			self.printArticle()
