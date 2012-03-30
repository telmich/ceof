#!/usr/bin/env python3
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
import socket

class Net(object):
    """
    This class handles the network connection to the chat server
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected = False

    def connect(self):
        """Connect to remote Chat Server"""
        try:
            self.socket = socket.create_connection((self.host, self.port))
        except socket.error as e:
            self.connected = False
            self.error = e
        else:
            self.connected = True

        return self.connected

        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.connect((self.host, int(self.port)))

    def disconnect(self):
        """Disconnect from chat server"""

        if self.connected:
            self.socket.close()

    def send(self, data):
        """Send data"""

        self.socket.sendall(data)
