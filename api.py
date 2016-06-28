from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
import queue

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
		self.pending_writes = queue.Queue()
		self.connected = True
		self.worker = Thread(target=self.worker_start)
		self.worker.daemon = True
		self.worker.start()
		APIServer.clients.append(self)

	def worker_start(self):
		timeout = 30 # seconds
		while self.connected:
			try:
				blocking = True
				message = self.pending_writes.get(blocking, timeout)
				self.sendMessage(message)
			except queue.Empty:
				pass

	# TODO: this probably isn't needed anymore, and don't want to waste threads on the tiny rpi
	def sendMessageAsync(self, message):
		self.pending_writes.put(message)

	def handleMessage(self):
		pass

	def handleClose(self):
		print(self.address, 'closed')
		self.connected = False
		APIServer.clients.remove(self)