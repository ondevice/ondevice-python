from ondevice.core import config, sock, service, state
from ondevice import control, modules

import filelock
import json
import logging
import os
import psutil
import sys
import traceback
import time


class Daemon(sock.Socket):
	""" Runs the ondevice daemon """
	def __init__(self, sid=None):
		self._abortMsg = None
		self.sid = sid

		key = config.getDeviceKey()
		params = {}
		if key != None:
			params['id'] = key
		if sid != None:
			params['sid'] = sid

		auth = (config.getDeviceUser(), config.getDeviceAuth())
		sock.Socket.__init__(self, '/serve', auth=auth, **params)

	def onMessage(self, msg):
		try:
			if not '_type' in msg:
				raise Exception("Missing message type: {0}".format(msg))
			elif msg._type == 'hello':
				assert not self._connectionSucceeded
				logging.info("Connection established, online as '%s'", msg.name)
				state.setAll('device', state='online', devId=msg.name)
				config.setDeviceId(msg.name)
				self.key = msg.devId
				self.sid = msg.sid
				config.setDeviceKey(msg.devId)

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
					svc = modules.getService(msg, self.key)

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
		state.remove('device', 'state', 'devId')
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

def getDaemonPID():
    pidfile = config._getConfigPath('ondevice.pid')
    if os.path.exists(pidfile):
        with open(pidfile, 'r') as f:
            rc = int(f.read().strip())
            if rc > 0 and psutil.pid_exists(rc):
				# TODO check if it's actually the right PID
                return rc

    return None

def runForever():
	""" Run the device endpoint in a loop (until it gets aborted) """
	lockPath = config._getConfigPath('ondevice.lock')
	lock = filelock.FileLock(lockPath)
	try:
		with lock.acquire(timeout=0):
			os.chmod(lockPath, 0o644)
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
		f.write('{0}\n'.format(os.getpid()))
		os.chmod(pidfile, 0o644)

	try:
		control.server.start()
		while (True):
			# TODO right now it's impossible to reuse Daemon objects (since the URL's set in the constructor but the device key might change afterwards)
			daemon = Daemon(sid=sid)
			if daemon.run() == True:
				state.setAll('device', state='reconnecting')
				retryDelay = 10
			if daemon._abortMsg != None:
				logging.info(daemon._abortMsg)
				break

			else:
				logging.info("Lost connection, retrying in %ds", retryDelay)
				time.sleep(retryDelay)
				retryDelay = min(900, retryDelay*1.5)
				sid = daemon.sid
	finally:
		control.server.stop()
		os.unlink(pidfile)
