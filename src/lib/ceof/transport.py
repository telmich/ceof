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

class CryptoError(ceof.Error):
    pass

class Transport(object):
    """Transport network packets"""

    def __init__(self, queue, interval):
        self.queue = queue
        self.interval = interval
        self.doexit = False


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
            except queue.Empty:
                text = self.noise()
                destination = self.random_recipient()

            # message = [recipient, message]

            self.send(message)
