from ondevice.core import state

import logging
import threading
import time

class ThreadInfo:
    """ Stores some information on each BackgroundThread instance """
    def __init__(self, **kwargs):
        for key in 'id,name'.split(','):
            if key not in kwargs:
                raise KeyError("Missing required ThreadInfo attribute: '{0}' (got: {1})", key, kwargs.keys())

        for k,v in kwargs.items():
            setattr(self, k, v)


class BackgroundThread():
    """ Thin wrapper around threading.Thread with simple event support.

    During the lifecycle of a backgrond thread the following events may occur (roughly in that order):
    - started: after a call to start()
    - running: before target() is being executed
    - stopping: after a call to stop()
    - finished: after target() has finished
    """
    def __init__(self, target, stopFn, name, args=(), kwargs={}):
        """ Create a BackgroundThread object
        - target: Thread function
        - stopFn: Function to gracefully stop the thread function (`target`) - will be called when invoking .stop()
        - name: Thread name (doesn't have to be unique)
        - args:  arguments to pass to target()
        - kwargs: keyword arguments to pass to target() """

        threadId = state.add('threads', 'seq', 1)
        self.info = ThreadInfo(name=name, id=threadId)

        self.target = target
        self.stopFn = stopFn
        self._listeners = {}
        self._thread = threading.Thread(target=self.run, name=name, args=args, kwargs=kwargs)

    def _emit(self, event, *args, **kwargs):
        listeners = list(self._listeners[event]) if event in self._listeners else []
        logging.debug("thread {0} fired event: {1} (args={2}, kwargs={3}, {4} listeners)".format(self.target, event, args, kwargs, len(listeners)))

        for l in listeners:
            l(*args, **kwargs)

    def run(self):
        """ Runs the target function (don't call this directly unless you want the target function be run in the current thread) """

        #
        state.add('threads', 'count', 1)
        self.info.startedAt = time.time()
        state.set('threads.info', self.info.id, self.info.__dict__)
        self._emit('running')
        try:
            self.target()
        finally:
            self._emit('finished')
            state.remove('threads.info', self.info.id)
            state.add('threads', 'count', -1)

    def addListener(self, event, fn):
        if event not in ['started', 'running', 'stopping', 'finished']:
            raise KeyError("Unsupported event: '{0}'".format(event))
        if not event in self._listeners:
            self._listeners[event] = set()

        self._listeners[event].add(fn)

    def addListenerObject(self, obj):
        """ Helper function to bind all signals to predefined methods of `obj` (if they exist)
         - mainly used for testing """
        fns = {'threadStarted': 'started', 'threadRunning':'running', 'threadStopping':'stopping', 'threadFinished':'finished'}
        for fn,event in fns.items():
            if hasattr(obj, fn):
                self.addListener(event, getattr(obj, fn))

    def removeListener(self, event, fn):
        if event not in self._listeners:
            return # Cant' remove something that isn't there
        self._listeners[event].remove(fn)

    def start(self):
        self._thread.start()
        self._emit('started')

    def stop(self):
        """ call the stopFn passed to the constructor and emit the 'stopping' signal """
        self.stopFn()
        self._emit('stopping')


class FixedDelayTask(BackgroundThread):
    """ Represents a repeating task that runs with a fixed delay (delay)
    in a background thread """

    def __init__(self, target, interval, name, *args, **kwargs):
        self._target = target
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._event = threading.Event()
        BackgroundThread.__init__(self, self._run, self._stop, name)

    def _run(self):
        while not self._event.wait(self.interval):
            try:
                self._target(*self.args, **self.kwargs)
            except:
                logging.exception('Exception in FixedDelayTask')

    def _stop(self):
        self._event.set()
