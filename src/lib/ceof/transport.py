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

import ceof
import logging
import queue
#import time

log = logging.getLogger(__name__)

class TransportError(ceof.Error):
    pass

class Transport(object):
    """Transport network packets"""

    def __init__(self, queue, interval, num_peers):

        # Receive real messages from here
        self.message_queue = queue

        # Get fake messages from here
        self.noise_queue = ceof.Noise()

        # Send every interal seconds (1/4 for instance)
        self.interval = interval

        # Have num_peers per route
        self.num_peers = num_peers

        
        self.doexit = False


    def route_to(self, peer):
        """Get num_peers without the current destination"""
        self.config.get_distinct_peers(self.num_peers, peer)

    def send(self, text, destination):
        """Send packet from queue"""

        path = self.create_route_to(destination)

        self.onion(...)?

    def _run(self):
        """Main loop"""

        while not self.doexit:
            # Try to get message, send noise otherwise
            try:
                text, destination = self.queue.get(True, interval)
                message = True
            except queue.Empty:
                message = False

            # ...... raise NoiseQueueEmptyError
            if not message:
                try:
                    text = self.noise_queue.get()
                except queue.Empty:
                    raise ceof.

                destination = self.random_recipient()
            # message = [recipient, message]

            self.send(message)
