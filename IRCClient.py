"""
IRCClient class to deal with connecting to server, input/output and
pinging

- Will add later, identification
"""
import socket
import sys
import os
import logging
import time
import re
import threading

class IRCClient:
	"""
	Client for IRC using the socket library
	"""
	def __init__(self, nickname, channels, network, rssobj):
		self.nickname = nickname
		self.channels = channels
		self.network = network
		self.rssobj = rssobj
		self.socket = None
		self.connected = False
		self.shownArticle = False
		self.talkBack = False # to make bot respond to messages
		self.pingcnt = 0 # keep count of ping for printing news
		self.ctx = {}

		# class logging setup
		self.loggingDIR = '{}/logs/'.format(
			os.path.dirname(os.path.realpath(__file__)))

		self.logger = logging.getLogger('newsirc.IRCClient')
		logFileHandler = logging.FileHandler(
			time.strftime(
				"{}IRCClient%m%d%Y.log".format(self.loggingDIR))
		)
		logFormat = logging.Formatter(
			"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		logFileHandler.setFormatter(logFormat)
		self.logger.addHandler(logFileHandler)

		self.logger.info('Running readFeed')
		self.rssobj.readFeed()

	def connect(self, ipass=None):
		"""
		start connection to IRC server
		"""
		# create socket connection
		self.logger.info("Open socket and connect to %s", self.network)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.network, 6667))

		# identify self with irc server
		self.send("NICK %s\r\n" % self.nickname)
		self.send("USER %(nick)s 0 * :newsbot IRC\r\n" % {
			'nick': self.nickname
		})

		self.logger.info("Starting loop to stay connected to server")

		while True:
			buf = str(self.socket.recv(2048)).strip('\r\n')
			lines = buf.splitlines()
			for data in lines:
				data = str(data).strip()

				if data == '':
					continue

				print("\n\nIN<", data)
				print("\n\n")

				args = data.split(None, 3)
				# print('args {}'.format(args))

				# server ping/pong
				if data.find('PING') != -1:
					self.logger.info("Ping recieved")
					self.pingcnt += 1
					print("\n\nPing found - cnt: {}\n\n".format(self.pingcnt))
					pnumber = data.split(':')[1]

					sthread = threading.Thread(target=self.send, kwargs={
						'msg': 'PONG :' + pnumber
					})
					sthread.start()

					# self.send('PONG :' + n)
					print("\n\nPong {} sent\n\n".format(pnumber))
					self.logger.info("Pong thread sent")

					# wait until 3rd ping to do after connected tasks
					# this will prevent joining when not all welcome messages
					# from the server are complete and blocking joining
					if self.connected is False and self.pingcnt == 3:
						self.perform()
						self.connected = True


				if len(args) == 4:
					self.ctx['sender'] = args[0][1:]

					# pulling sender out of network formatting
					# might be different on other networks
					if self.ctx['sender'].split('!'):
						self.ctx['sender'] = self.ctx['sender'].split('!')[0]
						self.ctx['sender'] = self.ctx['sender'].replace('\'', '')
						self.ctx['sender'] = self.ctx['sender'].replace(':', '')

					self.ctx['type'] = args[1]
					self.ctx['target'] = args[2]

					# strip message
					# might be different on other networks
					self.ctx['msg'] = args[3]
					# print(args[3])
					self.ctx['msg'] = self.ctx['msg'].replace(':', '')
					self.ctx['msg'] = self.ctx['msg'].replace('\r\n', '')
					self.ctx['msg'] = self.ctx['msg'].replace('\'', '')

					print(self.ctx)

				# registering - needs work
				if ipass:
					# print(self.ctx['type'])
					if self.ctx['type'] == '332':
						print('PRIVMSG nickserv identify %s' % ipass)
						self.send('PRIVMSG nickserv identify %s' % ipass)


				# private messages directed to the bot - not currently used
				# if self.ctx['type'] == 'PRIVMSG' and (
				# 	self.ctx['msg'].lower()[
				# 		0:len(self.nickname)] ==
				# 		self.nickname.lower() or self.ctx['target'] == self.nickname):

				if self.ctx:
					# thank for voice
					if '+v {}'.format(self.nickname) in self.ctx['msg'] and 'MODE' in self.ctx['type']:
						self.say(
							'thank you ~ <3',
							self.ctx['target']
						)

						# clear context
						self.ctx = {}

					# public messages directed to the bot
					elif self.talkBack and self.nickname.lower() in self.ctx['msg'].lower():
						# something is speaking to the bot
						query = self.ctx['msg']
						if self.ctx['target'] != self.nickname:
							query = query[len(self.nickname):]
							query = query.lstrip(':,;. ')

							# reply - later do some random replies like it is intelligent
							self.logger.info(
								'%s spoke to the bot in channel %s: %s',
								self.ctx['sender'],
								self.ctx['target'],
								query
							)

							# some basic commands
							if self.ctx['msg'] == '!test':
								self.logger.info(
									'!test command called by %s in channel %s',
									self.ctx['sender'],
									self.ctx['target']
								)

								self.say(
									'{}, fuck off :3'.format(self.ctx['sender']),
									self.ctx['target']
								)
							else:
								self.say(
									'{}, leave me alone >:0'.format(self.ctx['sender']),
									self.ctx['target']
								)

						# clear context
						self.ctx = {}

					# quit bot if disconnected from server
					elif 'ERROR' in self.ctx['sender'] and 'Closing' in self.ctx['type']:
						print(self.ctx)
						print('Closing IRCClient')
						exit()

					# clear context
					else:
						self.ctx = {}

				if self.pingcnt != 0 and (self.pingcnt % 4) == 0:
					print("pingcnt", self.pingcnt)
					# every 10th ping say news
					print("shownArticle", self.shownArticle)
					if self.shownArticle is False:
						print("say article!")
						self.sayArticle()
						self.shownArticle = True
				else:
					print("wait to say article..")
					self.shownArticle = False
					print("shownArticle", self.shownArticle)

	# IRC message protocol methods
	def send(self, msg):
		"""
		Send message to IRC server via socket
		"""
		print("OUT> {}".format(msg))
		self.socket.send(bytearray(msg+"\r\n", "utf-8"))

	def say(self, msg, to):
		"""
		Send private message to user on IRC server via socket
		"""
		sthread = threading.Thread(target=self.send, kwargs={
			'msg': "PRIVMSG %s :%s" % (to, msg)
		})
		sthread.start()

	def sayArticle(self):
		"""
		For sending RSS article to irc
		This assums it is in all the channels - will need to do some logic to check if really in channel
		"""
		for chan in self.channels:
			for artline in self.rssobj.printArticle():
				sthread = threading.Thread(target=self.send, kwargs={
					'msg': "PRIVMSG %s :%s" % (chan, artline)
				})
				sthread.start()

	def perform(self):
		"""
		Initial operations to perform when first connected
		Join channels
		"""
		self.send("MODE %s +x\r\n" % self.nickname)
		for chan in self.channels:
			self.send("JOIN %s\r\n" % chan)
			print('\n\nJoined {}\n\n'.format(chan))

	# bot methods
	def shutdown(self, channel=None):
		"""
		Shutdown bot command but not used
		Need to make a special users list that can only do this command
		"""
		if channel:
			self.send("QUIT %s" % channel)

		self.socket.close()
		sys.exit()
