""" stores non-persistent application state.

All functions in this module are thread safe """

import copy
import threading

_state = {}
_lock = threading.Lock()

def _getPath(path, create=False):
    global _state
    rc = _getPathRec(_state, path.split('.'), create)
    if rc == None:
        raise KeyError("state path not found: {0}".format(path))
    return rc

def _getPathOrNull(path):
    global _state
    return _getPathRec(_state, path.split('.'), False)

def _getPathRec(state, path, create=False):
    if len(path) == 0:
        return state
    key = path[0]
    if not key in state:
        if create:
            state[key] = {}
        else:
            return None

    return _getPathRec(state[key], path[1:], create)

def add(path, key, value):
    """ increment a state state value by a given integer (can be negative) """
    global _lock
    with _lock:
        parent = _getPath(path, True)
        if key not in parent:
            parent[key] = 0 # initialize with 0
        parent[key] += value
        return parent[key]

def getCopy():
    """ Returns a deep copy of the current state """
    global _lock, _state
    with _lock:
        return copy.deepcopy(_state)

def remove(path, *keys):
    """ Removes state keys, returning the number of keys actually removed """
    rc = 0

    global _lock
    with _lock:
        parent = _getPathOrNull(path)
        if parent != None:
            for key in keys:
                if key in parent:
                    del parent[key]
                    rc += 1

    return rc

def set(path, key, value):
    global _lock
    with _lock:
        parent = _getPath(path, True)
        parent[key] = value

def setAll(path, **kwargs):
    global _lock
    with _lock:
        parent = _getPath(path, True)
        for k,v in kwargs.items():
            parent[k] = v
