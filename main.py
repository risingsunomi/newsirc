"""
This is a re-write of my old bot at https://goo.gl/ekxnJS
into python3 and adding a logging library

risingsunomi
"""
import signal
import os
import sys
import logging
import time
import local
from RSS import RSS
from IRCClient import IRCClient

# signal from keyboard handler
def killKey(signum, frame):
	"""
	kill key being ctrl+c
	"""
	MAIN_LOGGER.info('Kill key manually called')
	sys.exit(0)

def app(nickname, channels, network):
	"""
	Where the news and irc client is placed
	"""
	MAIN_LOGGER.info('Initializing IRCClient with RSS')

	# rssobj = RSS('http://www.rssmix.com/u/8273687/rss.xml')
	# rssobj.readFeed()
	# print("\n\nrssobj entry - {}".format(rssobj.news_entries[0]))

	iclient = IRCClient(
		nickname=nickname,
		channels=channels,
		network=network,
		rssobj=RSS(local.RSSFEEDS)
	)

	MAIN_LOGGER.info('Connecting to irc server ')
	iclient.connect()


if __name__ == '__main__':
	"""
	This will run the bot and will have methods to connect, scrape rss and
	output
	"""

	# setup logging
	LOGGINGDIR = '{}/logs/'.format(
		os.path.dirname(os.path.realpath(__file__)))

	if not os.path.exists(LOGGINGDIR):
		os.makedirs(LOGGINGDIR)

	MAIN_LOGGER = logging.getLogger('newsirc.main')
	LOGFILEHANDLER = logging.FileHandler(
		time.strftime(
			"{}Main%m%d%Y.log".format(LOGGINGDIR))
	)
	LOGFORMAT = logging.Formatter(
		"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	LOGFILEHANDLER.setFormatter(LOGFORMAT)
	MAIN_LOGGER.addHandler(LOGFILEHANDLER)

	# add signal handling
	signal.signal(signal.SIGINT, killKey)

	MAIN_LOGGER.info('Running app method')
	app(local.NICKNAME, local.CHANNELS, local.SERVER)
