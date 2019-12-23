# -*- coding: utf-8 -*-
from configparser import ConfigParser
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler, HTTPStatus
import threading
import re
from pyrogram import Client
from httpserver import postable_simple_server


class bot_client:
	INFOMATCH = re.compile(r'/info\?[a-f\d]{64}')
	def __init__(self):
		self.config = ConfigParser()
		self.config.read('data/server_config.ini')

		self.client_pool = {}

		self.botapp = Client(
			'distributed_vps_control_bot',
			self.config['account']['api_id'],
			self.config['account']['api_key'],
			bot_token=self.config['account']['bot_key']
		)
		
		self.owner = int(self.config['account']['owner'])

		self.http_server = HTTPServer(
			(self.config['http']['addr'], self.config['http']['port']), postable_simple_server
		)


	
	def start(self):
		threading.Thread(target=self.http_server.serve_forever, daemon=True).start()
		self.botapp.start()

	def process_get(self, http_self: SimpleHTTPRequestHandler):
		if http_self.path.startswith('/info?'):
			if not self.INFOMATCH.match(http_self.path) or http_self.path.split('?')[-1] not in self.client_pool:
				http_self.send_error(HTTPStatus.FORBIDDEN, 'Authorized only')