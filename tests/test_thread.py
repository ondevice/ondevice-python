from unittest import TestCase
from ondevice.core import thread

import threading
import time

class GenericListener:
	""" Class that logs all method calls to self._log """
	class Method:
		def __init__(self, name, logFn):
			self.name = name
			self.logFn = logFn

		def __call__(self, *args, **kwargs):
			print("call to {0}:".format(self.name), args, kwargs)
			self.logFn({'name': self.name, 'ts': time.time(), 'args': args, 'kwargs': kwargs})

	def __init__(self):
		self._log = []

	def __getattr__(self, name):
		method = GenericListener.Method(name, self._log.append)
		setattr(self, name, method)
		return method

	def _hasEach(self, *args, **kwargs):
		""" returns True if each of the events from *args has occured once and each in **kwargs exactly the number of times of each param value """
		# convert args to kwargs ('foo' becomes {'foo': 1})
		for arg in args:
			if not arg in kwargs:
				kwargs[arg] = 1

		# go through the events we've capture
		data = {}
		for l in self._log:
			name = l['name']
			if not name in data: data[name] = 0
			data[name] += 1

		# compare them
		for event,count in kwargs.items():
			if event not in data:
				raise Exception("missing event: '{0}' ({1})".format(event, data))
			elif data[event] != count:
				raise Exception("event count mismatch (event={0}): expected={1}, actual={2}".format(event, count, data[event]))
			del data[event]

		# check unexpected events
		for ev, count in data.items():
			raise Exception("Got unexpected {0} events (count: {1})".format(ev, count))

class BackgroundThreadTest(TestCase):
	def _createThread(self, target, stopFn=None):
		""" creates and initializes a BackgroundThread instance with matching listener """
		listener = GenericListener()
		if target == None:
			target = listener.target
		if stopFn == None:
			stopFn = listener.stopFn
		rc = thread.BackgroundThread(target, stopFn, 'someThread')
		rc.addListenerObject(listener)
		rc._log = listener
		return rc

	def testSimpleTask(self):
		""" starts a BackgroundThread and makes sure its event handlers are called in the expected order """
		t = self._createThread(None)
		t.start()

		beforeStop = time.time()
		t.stop()

		t._log._hasEach('threadStarted', 'threadRunning', 'threadFinished', 'threadStopping', 'target', 'stopFn')

		return True


	def testStartStopTask(self):
		""" starts a task that'll run until it's being stopped manually """
		lock = threading.Lock()
		lock.acquire()
		# the second acquire call in the thread will block until we call release
		t = self._createThread(lock.acquire, lock.release)
		t.start()

		time.sleep(0.2)
		t._log._hasEach('threadStarted', 'threadRunning')

		t.stop()
		time.sleep(0.2)
		t._log._hasEach('threadStarted', 'threadRunning', 'threadStopping', 'threadFinished')

	def testStartFinishTask(self):
		""" same as above but the thread stops by itself (i.e. no 'stopping' event is triggered) """
		lock = threading.Lock()
		lock.acquire()

		t = self._createThread(lock.acquire)
		t.start()

		time.sleep(0.2)
		lock.release() # causes the thread target function to finish
		time.sleep(0.2)

		t._log._hasEach('threadStarted', 'threadRunning', 'threadFinished')

# TODO find a way to test FixedDelayTask in a predictable way
