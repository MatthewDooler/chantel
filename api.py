from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
import json

class APIServer:
	def __init__(self, port):
		self.websocket_server = SimpleWebSocketServer('', port, APIClient)
		self.websocket_server.clients = []
		t = Thread(target = self.websocket_server.serveforever, args = ())
		t.daemon = True
		t.start()
		print("API server initialised")

class APIClient(WebSocket):
	def handleConnected(self):
		print(self.address, 'connected')
		self.server.clients.append(self)

	def handleMessage(self):
		message = json.loads(self.data)
		print(message)

	def handleClose(self):
		print(self.address, 'closed')
		self.server.clients.remove(self)