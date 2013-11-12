# 2012-2013 Nico Schottelius (nico-ceof at schottelius.org)
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
import select
import queue
import socket
import multiprocessing
import urllib.parse
import time

log = logging.getLogger(__name__)

class Listener(object):
    """Listen server"""

    def __init__(self, listener, queue=None):
        self.listener = listener

        # Queue to put received packets into
        self.queue      = {}
        self.process    = {}
        self.fds        = []

        self.upstream_queue = queue

    # Start own process for each listener => use available cores!
    def run(self):
        for listener in self.listener:
            url = urllib.parse.urlparse(listener)

            address, port = url.netloc.split(":")
            name = "%s:%s" % (address, port)

            log.debug("Starting listener child %s" % name)

            self.queue[name]  = multiprocessing.Queue()
            self.process[name] = multiprocessing.Process(target=self.child, 
                args=(address, port, self.queue[name],))
            self.process[name].start()

            # File deskriptors for select()
            self.fds.append(self.queue[name]._reader)

        while True:
            for q in self.queue.values():
                data = False
                try:
                    data = q.get(block=False)
                except queue.Empty:
                    pass

                if data:
                    message = data.decode('utf-8')
                    self.upstream_queue.put(message)
                    log.debug("Forwarded message: %s to upstream" % (message))

            # Spinner - ugly, but not as ugly as searching for fds
            # returned by select and match on queue and get then...
            time.sleep(ceof.EOF_TIME_QPOLL)

        #p.join()

    def child(self, address, port, queue):
        log.debug("Running in child of listener for address %s:%s" % (address, port))
        self.child_queue = queue
        server = ceof.server.tcp.TCPServer(address, port, handler=self.child_handler)

        try:
            server.run()
        except socket.error as e:
            log.error("Failed to run listener on %s:%s: %s" % (address, port, e))

    def child_handler(self, conn, addr):
        log.debug("Connected by %s" % str(addr))

        data = []
        while 1:
            try:
                tmp = conn.recv(1024)
                if not tmp:
                    break
            
                data.append(tmp)

            except (socket.error, KeyboardInterrupt):
                conn.close()
                raise

        # Done, send data
        message = b''.join(data)
        log.debug("Submitting data to parent: %s" % message.decode('utf-8'))
        self.child_queue.put(message)
        conn.close()
