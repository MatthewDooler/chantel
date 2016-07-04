from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread

class APIServer:
	clients = []  # TODO: make this an instance variable, by linking clients back to servers (if possible)
	def __init__(self, port):
		websocket_server = SimpleWebSocketServer('', port, APIClient)
		t = Thread(target = websocket_server.serveforever, args = ())
		t.daemon = True
		t.start()
		print("API server initialised")

class APIClient(WebSocket):
	def handleConnected(self):
		print(self.address, 'connected')
		APIServer.clients.append(self)

	def handleMessage(self):
		pass

	def handleClose(self):
		print(self.address, 'closed')
		APIServer.clients.remove(self)