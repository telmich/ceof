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
import select
import multiprocessing
import urllib.parse

log = logging.getLogger(__name__)

#class ServerError(ceof.Error):
#    pass

class Listener(object):
    """Listen server"""

    def __init__(self, listener, queue=None):
        self.listener = listener

        # Queue to put received packets into
        self.queue      = {}
        self.process    = {}
        self.fds        = []

    # Start own process for each listener => use available cores!
    def run(self):
        for listener in self.listener:
            url = urllib.parse.urlparse(listener)

            address, port = url.netloc.split(":")
            name = address + port

            print("Listening on %s:%s" % (address, port))
            print(self.queue)
            print(type(self.queue))

            self.queue[name]  = multiprocessing.Queue()
            self.process[name] = multiprocessing.Process(target=self.child, 
                args=(address, port, self.queue[name],))
            self.process[name].start()

            # File deskriptors for select()
            self.fds.append(self.queue[name]._reader)

        # wait for input
        (select_res,[],[]) = select.select(self.fds,[],[])

        #p.join()

    def child(self, address, port, queue):
        print("running in child")
        server = ceof.server.tcp.TCPServer(address, port)
        server.run()
