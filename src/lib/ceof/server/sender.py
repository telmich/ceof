# 2012 Nico Schottelius (nico-ceof at schottelius.org)
#
# This file is part of ceof.
#
# ceof is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ceof is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ceof. If not, see <http://www.gnu.org/licenses/>.
#
#


import ceof
import logging
import queue
import time

log = logging.getLogger(__name__)

class SenderError(ceof.Error):
    pass

class Sender(object):
    """Sender server"""

    def __init__(self, interval, queue, noise_dir, peer_dir, gpg_config_dir, send_noise=True):
        self.interval = interval

        self._upstream_queue = queue
        self._noise = ceof.noise.Server(noise_dir, False, peer_dir, gpg_config_dir)
        self._send_noise = send_noise

        self._noise.start()

    def run(self):
        """Main loop"""

        log.debug("Sender child started")

        while True:
            log.debug("Sender polling for data to be sent")
            # Try to get message, send noise otherwise
            try:
                destination, pkg = self._upstream_queue.get(block=False)
                message = True
            except queue.Empty:
                message = False

            if not message and self._send_noise:
                log.debug("No message received - acquiring noise")
                destination, pkg = self._noise.get()
                message = True

            try:
                if message:
                    self.send(destination, pkg)
            except SenderError as e:
                log.warn(e)

            time.sleep(self.interval)

    @staticmethod
    def send(address, pkg):
        """Send out message"""

        # FIXME: remove hard coded tcp
        log.debug("Sending message %s to %s" % (str(pkg), str(address)))

        import socket
        import urllib.parse
        url = urllib.parse.urlparse(address)
        host, port = url.netloc.split(":")
        host = "127.0.0.1"
        try:
            mysocket = socket.create_connection((host, port))
        except socket.error as e:
            raise SenderError("Cannot connect to %s: %s" % ((host, port), e))

        network_pkg = ceof.encode(pkg)
        mysocket.sendall(network_pkg)
        mysocket.close()

