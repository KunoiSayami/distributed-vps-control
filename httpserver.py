from http.server import SimpleHTTPRequestHandler, HTTPServer

class postable_simple_server(SimpleHTTPRequestHandler):

	conn = None

	def process_get(self):
		return False

	def process_post(self, file_str: str) -> str:
		return ''

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
		return_payload = self.process_post(self.rfile.read(int(self.headers['Content-Length'])))
		self.wfile.write(return_payload)

if __name__ == "__main__":
	server = HTTPServer(('127.0.0.1', 8080), postable_simple_server)
	server.serve_forever()
