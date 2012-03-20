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
# Generic TCP Server to be used for UI Server
#
#

import ceof
import ceof.tcpserver
import logging
import socket

log = logging.getLogger(__name__)

class UIServer(object):
    """Server to accept UI connections"""

    def __init__(self, address, port):
        self.tcpserver = ceof.tcpserver.TCPServer(address, port, self.handler)

    def run(self):
        self.tcpserver.run()

    def handler(self, data):
        """Handle incoming data"""
        print(data)
