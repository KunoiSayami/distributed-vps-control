# -*- coding: utf-8 -*-
# httpserver.py
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
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json

class postable_simple_server(SimpleHTTPRequestHandler):

	def process_get(self):
		return False

	def process_post(self, _payload: str) -> dict:
		return {}

	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def do_GET(self):
		"""Serve a GET request."""
		if postable_simple_server.process_get(self):
			return
		f = self.send_head()
		if f:
			try:
				self.copyfile(f, self.wfile)
			finally:
				f.close()

	def do_POST(self):
		self._set_headers()
		payload = json.load(self.rfile.read(int(self.headers['Content-Length'])))
		return_payload = self.process_post(payload)
		self.wfile.write(json.dumps(return_payload))

if __name__ == "__main__":
	server = HTTPServer(('127.0.0.1', 8080), postable_simple_server)
	server.serve_forever()
