"""
Attempts to gracefully stop a running ondevice daemon

After sending the terminate signal, it'll wait for up to five seconds for the
daemon to stop.
Only if the daemon was running, it'll return 0

Returns:
- 0 on success
- 1 on exceptions (if you encounter those, let us know)
- 2 if the daemon wasn't running
- 3 on timeout
- >3 might be used in the future
"""

usage = {
    'msg': 'Stop a running ondevice daemon',
    'group': 'device'
}

from ondevice.core import config

import os
import psutil
import signal
import sys
import time

def run():
    pid = config.getDaemonPID()
    if pid != None:
        sys.stderr.write("Stopping ondevice daemon...")
        sys.stderr.flush()

        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError as e:
            sys.stderr.write("\nondevice daemon isn't running (stale pid: {0})\n".format(pid))
            return 2

        # effective timeout: 5sec (20*250ms)
        for i in range(20):
            if not psutil.pid_exists(pid):
                sys.stderr.write("done\n")
                return 0 # stopped it successfully

            sys.stderr.write('.')
            sys.stderr.flush()
            time.sleep(0.25)

        sys.stderr.write("\nERROR: Timeout while trying to stop ondevice daemon (pid: {0})\n".format(pid))
        return 3

    else:
        sys.stderr.write("ERROR: ondevice daemon isn't running\n")
        return 2
