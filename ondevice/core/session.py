from ondevice.core import config, sock, service
from ondevice import modules

import filelock
import json
import logging
import os
import sys
import traceback
import time


class Session(sock.Socket):
	""" Connects to the ondevice service """
	def __init__(self, sid=None):
		self._abortMsg = None
		self.sid = sid

		devId = config.getDeviceId()
		kwargs = {}
		if devId != None:
			kwargs['id'] = devId
		if sid != None:
			kwargs['sid'] = sid

		auth = (config.getDeviceUser(), config.getDeviceAuth())
		sock.Socket.__init__(self, '/serve', auth=auth, **kwargs)

	def onMessage(self, msg):
		try:
			if not '_type' in msg:
				raise Exception("Missing message type: {0}".format(msg))
			elif msg._type == 'hello':
				assert not self._connectionSucceeded
				logging.info("Connection established, online as '%s'", msg.name)
				config.setDeviceName(msg.name)
				self.devId = msg.devId
				self.sid = msg.sid
				config.setDeviceId(msg.devId)

				for name, svc in service.listServices().items():
					self.send({'_type': 'announce', 'name': name, 'protocol': svc['protocol']})

				self._connectionSucceeded = True
			elif msg._type == 'ping':
				# send back a 'pong' message
				logging.debug("Got ping: %s", repr(msg))
				response = {'_type': 'pong', 'ts': msg.ts}
				self.send(response)
			elif msg._type == 'connect':
				logging.info("Got '%s' request by user %s (ip: %s)", msg.service, msg.clientUser, msg.clientIp)
				try:
					errTpl = {'_type': 'connectError', 'tunnelId': msg.tunnelId}
					if not service.exists(msg.service):
						return self.sendConnError(404, "Service '{0}' not found".format(msg.service), msg.tunnelId)
					proto = service.get(msg.service)['protocol']
					if msg.protocol != proto:
						return self.sendConnError(400, "Protocol mismatch (expected={0}, actual={1})".format(proto, msg.protocol), msg.tunnelId)
					elif not modules.exists(proto):
						return self.sendConnError(404, "Module '{0}' not found!".format(msg.protocol), msg.tunnelId)
					svc = modules.getService(msg, self.devId)

					svc.startRemote()
					svc.startLocal()
				except Exception as e:
					# got error -> notify the server
					self.send({'_type': 'connectError', 'tunnelId': msg.tunnelId, 'code': 502, 'msg': repr(e)})
					raise e

			elif msg._type == 'error':
				errType = 'Error'
				if msg.code == 400: errType = 'Bad Request'
				elif msg.code == 403: errType = 'Forbidden'
				elif msg.code == 404: errType = 'Not Found'

				logging.error("%s: %s", errType, msg.msg)
			else:
				logging.error("onMessage: unsupported type")
				logging.error("  msg=%s", msg)
		except Exception as e:
			# the websocket-client lib swallows the stack traces of exceptions
			print("Msg: '{0}'".format(msg))
			traceback.print_exc()
			raise e

	def _onError(self, ws, error):
		if type(error) is KeyboardInterrupt:
			self._abortMsg = "Keyboard interrupt, exiting"
			return

		sock.Socket._onError(self, ws, error)

	def run(self):
		self._connectionSucceeded = False
		sock.Socket.run(self)
		return self._connectionSucceeded

	def send(self, msg):
		data = json.dumps(msg)
		logging.debug('>> %s', data)
		self._ws.send(data)

	def send2(self, **kwargs):
		self.send(kwargs)

	def sendConnError(self, code, msg, tunnelId):
		logging.error("Connection error: {0} (code {1})".format(msg, code))
		self.send2(_type='connectError', tunnelId=tunnelId, code=code, msg=msg)

def runForever():
	""" Run the device endpoint in a loop (until it gets aborted) """
	lock = filelock.FileLock(config._getConfigPath('ondevice.lock'))
	try:
		with lock.acquire(timeout=0):
			_runForever()
	except filelock.Timeout:
		logging.error("There's already another instance of `ondevice daemon` running!")
		sys.exit(1)

def _runForever():
	""" runForever() internals without the lock file mechanism """
	retryDelay = 10
	sid = None

	pidfile = config._getConfigPath('ondevice.pid')
	with open(pidfile, 'w') as f:
		f.write(str(os.getpid()))

	try:
		while (True):
			# TODO right now it's impossible to reuse Session objects (since the URL's set in the constructor but the devId might change afterwards)
			session = Session(sid=sid)
			if session.run() == True:
				retryDelay = 10
			if session._abortMsg != None:
				logging.info(session._abortMsg)
				break

			else:
				logging.info("Lost connection, retrying in %ds", retryDelay)
				time.sleep(retryDelay)
				retryDelay = min(900, retryDelay*1.5)
				sid = session.sid
	finally:
		os.unlink(pidfile)
