# -*- coding: utf-8 -*-
#
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


import ceof.server.listener
#import ceof.server.ui
import logging
import multiprocessing
import queue
import time

from ceof.server.listener import Listener

log = logging.getLogger(__name__)


#from ceof.server.listener import Listener

class Server(object):
    """
    Combine all servers:

    - Listener (for incoming packets)
    - Sender (for sending packets regulary)
    - UI (for handling user input)

    """

    def __init__(self, config, listener=True, sender=True, ui=True,
        ui_addr='127.0.0.1', ui_port='4242'):

        self.config = config
        self.queue  = {}
        self.server = {}
        self.process = {}
        self.handler = {}

        self.listener = listener
        self.sender = sender
        self.ui = ui
        self.ui_addr = ui_addr
        self.ui_port = ui_port

        self._init_listener()
        #self._init_sender()
        #self._init_ui()

    @staticmethod
    def commandline(args, config):
        log.debug(args)

        server = Server(config, args.no_listener, args.no_sender, args.no_ui,
            args.ui_address, args.ui_port)

        server.run()

    def _init_listener(self):
        if self.listener:
            listener = ceof.Listener(self.config.listener)
            self.queue['listener']  = multiprocessing.Queue()
            self.server['listener'] = Listener(listener.listener, 
                self.queue['listener'])
            self.process['listener'] = multiprocessing.Process(target=self.server['listener'].run)
            self.handler['listener'] = self.listen_handler


    def run(self):
        """Run specified servers"""

        log.debug("run,....")

        # Start servers in their subprocesses
        for name, process in self.process.items():
            log.debug("Starting process of %s" % name)
            process.start()

        # Iterate over input from servers
        while True:
            for name, q in self.queue.items():
                log.debug("Polling on %s queue" % name)
                data = False
                try:
                    data = q.get(block=False)
                except queue.Empty:
                    pass

                if data:
                    log.debug("Got message from: %s:%s" % (name, data))
                    self.handler[name](data)

            # Spinner - ugly, but not as ugly as searching for fds
            # returned by select and match on queue and get then...
            log.debug("loop,....")
            time.sleep(0.5)

        # FIXME: Kill and join on exit
        for process in self.process.values():
            process.join()

    def listen_handler(self, message):
        """Handle incoming packet from listener"""
        log.debug("Handling incoming message from listener: %s" % message)
