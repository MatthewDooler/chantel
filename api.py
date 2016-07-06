from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
import json

class APIServer:
	def __init__(self, port, props):
		self.props = props
		self.clients = []
		self.websocket_server = SimpleWebSocketServer('', port, APIClient)
		self.websocket_server.api_server = self
		t = Thread(target = self.websocket_server.serveforever, args = ())
		t.daemon = True
		t.start()
		print("API server initialised")

class APIClient(WebSocket):
	def handleConnected(self):
		print(self.address, 'connected')
		self.server.api_server.clients.append(self)

	def handleMessage(self):
		throttle = json.loads(self.data)
		self.server.api_server.props.setDesiredThrottle(throttle["0"], throttle["1"], throttle["2"], throttle["3"])

	def handleClose(self):
		print(self.address, 'closed')
		self.server.api_server.clients.remove(self)