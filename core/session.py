import json
import logging
import modules
import threading
import traceback
import sys

from core import config, sock, service

class Session(sock.Socket):
	""" Connects to the ondevice service """
	def __init__(self, auth):
		devId = config.getDeviceId()
		kwargs = {}
		if devId != None:
			kwargs['id'] = devId

		if auth != None:
			config.setDeviceAuth(auth)
		else:
			auth = config.getDeviceAuth()
			if auth == None:
				logging.error("Missing authentication key. You'll have to set it once using the 'auth=...' param")
				sys.exit(1)

		kwargs['auth'] = auth
		super().__init__('/serve', **kwargs)

	def onMessage(self, msg):
		try:
			if not '_type' in msg:
				raise Exception("Missing message type: {0}".format(msg))
			elif msg._type == 'hello':
				assert not hasattr(self, '_devId') and not hasattr(self, '_sid')
				logging.debug("Got hello: %s", repr(msg))
				self._devId = msg.devId
				self._sid = msg.sid
				config.setDeviceId(msg.devId)

				for name, svc in service.listServices().items():
					self.send({'_type': 'announce', 'name': name, 'protocol': svc['module']})

			elif msg._type == 'ping':
				# send back a 'pong' message
				logging.debug("Got ping: %s", repr(msg))
				response = {'_type': 'pong', 'ts': msg.ts}
				self.send(response)
			elif msg._type == 'connect':
				logging.info("Got connection request (%d active threads)", threading.active_count())
				logging.debug("  Message data: %s", repr(msg))
				svc = modules.getService(msg, self._devId)
				# TODO synchronize the both of them (e.g. only call startLocal after the remote connection is up)
				svc.startRemote()
				svc.startLocal()

			else:
				logging.error("onMessage: unsupported type")
				logging.error("  ws=%s", ws)
				logging.error("  msg=%s", msg)
		except Exception as e:
			# the websocket-client lib swallows the stack traces of exceptions
			print("Msg: '{0}'".format(msg))
			traceback.print_exc()
			raise e

	def send(self, msg):
		data = json.dumps(msg)
		logging.debug('>> %s', data)
		self._ws.send(data)
