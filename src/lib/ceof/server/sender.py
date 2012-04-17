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

    def __init__(self, interval, queue, noise_dir, peer_dir):
        self.interval = interval

        self._upstream_queue = queue
        self._noise = ceof.Noise(noise_dir)
        # FIXME: remove start(), do automatically on startup, fix commandline
        self._noise.start()
        self._peer_dir = peer_dir

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

            if not message:
                log.debug("No message received")
                try:
                    # FIXME: need to create onion packet from it!
                    pkg = self._noise.get()
                    log.debug("Noise: %s" % pkg)
                    pkg = ceof.encode(pkg)
                except queue.Empty:
                    raise NoiseQueueEmptyError

                destination = self.random_peer_random_address()

            try:
                if message:
                    self.send(destination, pkg)
            except SenderError as e:
                log.warn(e)

            time.sleep(self.interval)

    def random_peer_random_address(self):
        """Return a random address of a random peer"""
        peers = ceof.Peer.list_random_peers(self._peer_dir, 1)

        address = peers[0].random_address()

        log.debug("Seleted random address %s" % address)
        return address

    def send(self, address, pkg):
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

        mysocket.sendall(pkg)
        mysocket.close()

