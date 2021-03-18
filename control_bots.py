# -*- coding: utf-8 -*-
# control_bots.py
# Copyright (C) 2017-2020 KunoiSayami
#
# This module is part of WelcomeBot-Telegram and is released under
# the AGPL v3 License: https://www.gnu.org/licenses/agpl-3.0.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import re
import threading
from configparser import ConfigParser
from http.server import HTTPServer, SimpleHTTPRequestHandler

from pyrogram import (CallbackQuery, CallbackQueryHandler, Client, Filters,
                      InlineKeyboardButton, InlineKeyboardMarkup, Message,
                      MessageHandler)

from httpserver import PostableSimpleServer
from utils import mysqldb


class RewritedServer(PostableSimpleServer):
	INFOMATCH = re.compile(r'/info\?[a-f\d]{64}')
	bot_self = None
	def process_get(self, payload: SimpleHTTPRequestHandler) -> bool:
		return False

	def process_post(self, payload: dict) -> dict:
		if self.path == '/register':
			# {username: str}
			real_ip = self.headers.get('X-Real-IP', '127.0.0.1')
			rt = mysqldb.get_instance().insert_new_client(payload.get('username'), real_ip)
			payload.update({'ip': real_ip})
			BotClient.get_inistance().request_confirm(rt.cid, payload)
			return {'status': 200, 'code': 1, 'uid': rt.uid}
		elif self.path == '/fetch':
			# {username: str, uid: int}
			if mysqldb.get_instance().query_approve_status(payload):
				return {'status': 200, 'code': 2}
			return {'status': 200, 'code': 300}

class _BotClient:
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

		self.conn = mysqldb.init_instance(
			self.config['mysql']['host'],
			self.config['mysql']['user'],
			self.config['mysql']['password'],
			self.config['mysql']['database']
		)

		self.owner = self.config.getint('account', 'owner')

		self.http_server = HTTPServer(
			(self.config['http']['addr'], self.config['http']['port']), RewritedServer
		)

		self.http_thread = None
		self._basic_filter = Filters.chat(self.owner)

	def init_handle(self):
		self.botapp.add_handler(MessageHandler(self.handle_status, self._basic_filter))
		self.botapp.add_handler(CallbackQueryHandler(self.handle_callback_query))

	def idle(self):
		try:
			self.botapp.idle()
		except InterruptedError:
			pass

	def handle_status(self, _client: Client, _msg: Message):
		pass

	def request_confirm(self, cid: int, payload: dict):
		self.botapp.send_message(self.owner, 'Do you want to approve this machine\n**Username**: `{}`\nIP Address:`{}`'.format(
			payload.get('username'), payload.get('ip')
		), 'markdown', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
			InlineKeyboardButton('approve', callback_data=f'approve {cid}')
		]]))

	def start(self):
		self.http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
		self.http_thread.start()
		self.botapp.start()

	def handle_callback_query(self, client: Client, msg: CallbackQuery):
		data = msg.data.split()
		if data[0] == 'approve':
			self.conn.approve_new_client(data[1])

	def stop(self):
		self.botapp.stop()
		self.conn.close()

class BotClient(_BotClient):
	_bot_self = None
	@staticmethod
	def get_inistance() -> _BotClient:
		if BotClient._bot_self is None:
			BotClient._bot_self = BotClient()
		return BotClient._bot_self
	
	@staticmethod
	def init_instance() -> _BotClient:
		return BotClient._bot_self

if __name__ == "__main__":
	bot = BotClient.get_inistance()
	bot.start()
	bot.idle()
	bot.stop()
