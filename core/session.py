import json
import modules
import threading
import traceback
import websocket

from core import sock
from core import service

class Session(sock.Socket):
	""" Connects to the ondevice service """
	def __init__(self, auth, dev):
		super().__init__('/serve', auth=auth, dev=dev)

	def onMessage(self, msg):
		try:
			if not '_type' in msg:
				raise Exception("Missing message type: {0}".format(msg))
			elif msg._type == 'hello':
				print("Got hello: "+repr(msg))
				for name, svc in service.listServices().items():
					self.send({'_type': 'announce', 'name': name, 'protocol': svc['module']})

			elif msg._type == 'ping':
				# send back a 'pong' message
				#print("Got ping: "+repr(msg))
				response = {'_type': 'pong', 'ts': msg.ts}
				self.send(response)
			elif msg._type == 'connect':
				print("Got connection request ({0} active threads): {1}".format(threading.active_count(), repr(msg)))
				svc = modules.getService(msg)
				t = threading.Thread(target=svc.run)

			else:
				print("onMessage: unsupported type")
				print("  ws={0}".format(ws))
				print("  msg={0}".format(msg))
		except Exception as e:
			# the websocket-client lib swallows the stack traces of exceptions
			print("Msg: '{0}'".format(msg))
			traceback.print_exc()
			raise e
