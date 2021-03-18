# -*- coding: utf-8 -*-
# utils.py
# Copyright (C) 2019-2020 KunoiSayami
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
import uuid
from configparser import ConfigParser

import pymysql
import requests

from libpy3.mysqldb import mysqldb as _mysqldbEx


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

class clientObj:
	def __init__(self, cid: int, uid: str):
		self._uid = uid
		self._cid = cid

	@property
	def uid(self):
		return self._uid

	@property
	def cid(self):
		return self._cid

class _mysqldb(_mysqldbEx):
	def insert_new_client(self, username: str, ip: str) -> clientObj:
		uid = uuid.uuid4()
		self.execute("INSERT INTO `pending_client` (`username`, `ip`, `uid`) VALUE (%s, %s, %s)", (username, ip, uid))
		return clientObj(self.query1("SELECT LAST_INSERT_ID()")['LAST_INSERT_ID()'], uid)

	def _insert_new_approved_client(self, client_id: int, username: str, ip: str, uid: str):
		self.execute("INSERT INTO `client_pool` (`client_id`, `username`, `ip`, `uuid`) VALUE (%s, %s, %s, %s)",
			(client_id, username, ip, uid))

	def approve_new_client(self, pool_id: int):
		sqlObj = self.query1("SELECT * FROM `pending_client` WHERE `id` = %s", pool_id)
		if sqlObj is not None:
			self._insert_new_approved_client(pool_id, sqlObj['username'], sqlObj['ip'], sqlObj['uid'])
		return None

	def query_approve_status(self, payload: dict) -> bool:
		return self._query_approve_status(payload.get('username'), payload.get('uid'))

	def _query_approve_status(self, username: str, uid: str) -> bool:
		return self.query1("SELECT * FROM `client_pool` WHERE `username` = %s AND `uid` = %s", (username, uid)) is not None

class mysqldb(_mysqldb):
	_self = None
	@staticmethod
	def init_instance(
		host: str,
		user: str,
		password: str,
		db: str,
		charset: str = 'utf8mb4',
		cursorclass = pymysql.cursors.DictCursor,
		autocommit = False
	) -> _mysqldb:
		mysqldb._self = _mysqldb(host, user, password, db, charset, cursorclass, autocommit)
		return mysqldb._self
	
	@staticmethod
	def get_instance() -> _mysqldb:
		return mysqldb._self
