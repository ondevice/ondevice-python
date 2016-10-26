"""
Tunneled SSH client module

Usage:
- {cmd} ssh <deviceId> [ssh-arguments...]
- {cmd} ssh <user>@<deviceId> [ssh-arguments...]


Examples:
- {cmd} ssh root@test
  connect to SSH on your `test` device as user `root`
"""


from ondevice.modules import ModuleClient, ModuleService

import errno
import logging
import socket
import subprocess
import sys

info = 'Connect to your devices\' SSH server'
encrypted = True

# DEPRECATED - use `ondevice ssh` instead
class Client(ModuleClient):
    """ Endpoint stub that simply invokes 'ssh' with the ProxyCommand set to
    'onclient connect ssh:tunnel' """

    def runLocal(self, *args):
        info = self._info
        devId = info.devId
        protocol = info.protocol
        svcName = info.service

        # TODO use the dynamic module name
        proxyCmd = [ sys.argv[0], 'connect', '{0}:tunnel@{1}'.format(protocol, svcName), devId ]

        ssh = subprocess.Popen(['ssh', '-o', 'ProxyCommand={0}'.format(' '.join(proxyCmd)), 'ondevice:{0}'.format(devId)]+list(args), stdin=None, stdout=None, stderr=None)
        return ssh.wait()

    def startRemote(self):
        pass # we don't need a remote connection; Client_tunnel does that for us

class Client_tunnel(ModuleClient):
    def onMessage(self, data):
        logging.debug("onMessage: %s", repr(data))
        stream = self.getConsoleBuffer(sys.stdout)
        stream.write(data)
        stream.flush()

    def onClose(self):
        logging.debug('ondevice ssh: connection closed, exiting')
        sys.exit(0)

    def onEOF(self):
        logging.debug('ondevice ssh: got EOF, closing stdout')
        self.getConsoleBuffer(sys.stdout).close()


    def runLocal(self):
        while True:
            # read1() only invokes the underlying read function only once (and
            # in contrast to read() returns as soon as there's data available,
            # not just when 4096 bytes have actually been read)
            stream = self.getConsoleBuffer(sys.stdin)
            data = stream.read1(4096)
            if data:
                logging.debug("sndData: %s", repr(data))
                self._conn.send(data)
            else:
                logging.info("Local EOF, closing connection")
                self._conn.sendEOF()
                return

class Service(ModuleService):
    def runLocal(self):
        """ Connect to the local SSH server (on port 22) and send all data we get from it over the tunnel """
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO make host+port configurable
        # TODO use a timeout; raise an exception on error
        self._sock.connect(('localhost', 22))
        logging.debug("connected to SSH server: {0} -> {1}".format(self._sock.getsockname(), self._sock.getpeername()))

        while True:
            try:
                data = self._sock.recv(4096)
                if data:
                    logging.debug("sndData: %s", repr(data))
                    self._conn.send(data)
                else:
                    self._conn.sendEOF()
                    return
            except OSError as e:
                if e.errno == errno.EBADF:
                    # socket has been closed (i.e. by onClose())
                    break
                else: raise e

    def stopLocal(self):
        """ stops the loop in runLocal() by closing the SSH socket """
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

    def onClose(self):
        ModuleService.onClose(self)
        logging.debug("closing SSH client socket ({0} -> {1})".format(self._sock.getsockname(), self._sock.getpeername()))
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

    def onMessage(self, data):
        logging.debug("onMessage: %s", repr(data))
        self._sock.send(data)
