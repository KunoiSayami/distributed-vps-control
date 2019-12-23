# -*- coding: utf-8 -*-
from configparser import ConfigParser
import requests

class clientQuery:
	def __init__(self):
		self.config = ConfigParser()
		self.config.read('data/config.ini')
		
		if self.config['proxy']['address'] != '':
			proxy_uri = 'http://{}:{}/'.format(self.config['proxy']['address'],
				self.config['proxy']['port'])

			self.proxies = {'http': proxy_uri, 'https': proxy_uri}
		else:
			self.proxies = {}
		
		self.address = self.config['server']['address']
		self.uuid = self.getUUID()

	@staticmethod
	def getUUID() -> str:
		try:
			with open('data/.uuid') as fin:
				return fin.read()
		except FileNotFoundError:
			return None

	def check_connect(self):
		requests.post(self.address, proxies=self.proxies)

	@staticmethod
	def get_system_information() -> str:
		pass

