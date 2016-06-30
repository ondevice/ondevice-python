import json
import traceback
import websocket

from core import service

class Message:
	def __init__(self, data):
		assert type(data) == dict
		self._data = data

	def __contains__(self, key): return key in self._data
	def __getattr__(self, key): return self._data[key]
	def __repr__(self): return "Message({0})".format(self._data)

class Session:
	""" Connects to the ondevice service """
	def __init__(self, auth, dev, url="ws://localhost:8080/v0.10/serve/websocket"):
		# TODO implement proper URL handling
		self._url = '{0}?auth={1}&id={2}'.format(url, auth, dev)
		self._ws = websocket.WebSocketApp(self._url,
			on_message=self._onMessage,
			on_error=self._onError,
			on_open=self._onOpen,
			on_close=self._onClose)

	def _onClose(self, ws):
		print("onClose:")
		print("  ws={0}".format(ws))

	def _onError(self, ws, error):
		print("onError:")
		print("  ws={0}".format(ws))
		print("  error={0}".format(error))

	def _onMessage(self, ws, messageText):
		try:
			print("<< {0}".format(messageText))
			msg = Message(json.loads(messageText))

			if not '_type' in msg:
				raise Exception("Missing message type: {0}".format(messageText))
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
				print("Got connection request: "+repr(msg))

			else:
				print("onMessage: unsupported type")
				print("  ws={0}".format(ws))
				print("  msg={0}".format(msg))
		except Exception as e:
			# the websocket-client lib swallows the stack traces of exceptions
			print("Msg: '{0}'".format(messageText))
			traceback.print_exc()
			raise e

	def _onOpen(self, ws):
		print("onOpen:")
		print("  ws={0}".format(ws))

	def run(self):
		self._ws.run_forever()

	def send(self, msg):
		data = json.dumps(msg)
		print('>> {0}'.format(data))
		self._ws.send(data)
