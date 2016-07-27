from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
import json
import os
import sys

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
		message = json.loads(self.data)
		if "throttle" in message:
			throttle = message["throttle"]
			self.server.api_server.props.setDesiredThrottle(throttle["0"], throttle["1"], throttle["2"], throttle["3"])
		elif "ping" in message:
			ping = message["ping"]
			self.sendMessage(json.dumps({"ping": ping}))
		elif "restart" in message:
			restart()
		elif "shutdown" in message:
			restart()

	def handleClose(self):
		print(self.address, 'closed')
		self.server.api_server.clients.remove(self)

def restart():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def shutdown():
    os.system("shutdown now -h")
