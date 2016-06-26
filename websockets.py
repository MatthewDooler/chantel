#!/usr/bin/env python3
import sys
import datetime as dt
import time
import math
import argparse
import json

from threading import Thread
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

clients = []
class StatReporter(WebSocket):

    def handleMessage(self):
        pass

    def handleConnected(self):
        print(self.address, 'connected')
        clients.append(self)

    def handleClose(self):
        print(self.address, 'closed')

server = SimpleWebSocketServer('', 8080, StatReporter)

print("Starting websocket server...")
wsthread = Thread(target = server.serveforever, args = ())
wsthread.start()
print("Done")

heading = 5
pitch = 2
roll = 4

while True:
	for client in clients:
		message = {
			'heading': heading,
			'pitch': pitch,
			'roll': roll
		}
		client.sendMessage(json.dumps(message))
	time.sleep(1)

wsthread.join()