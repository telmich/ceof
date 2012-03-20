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
import logging
import socket

log = logging.getLogger(__name__)

class TCPServerError(ceof.Error):
    pass

class TCPServer(object):
    """Server to accept connections"""

    def __init__(self, address, port, handler):
        self.address        = address
        self.port           = port
        self.data_handler   = handler

    def run(self):
        """Main loop"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        log.info("Running Server on %s:%s" % (self.address, self.port))
        s.bind((str(self.address), int(self.port)))
        s.listen(1)

        try:
            while 1:
                conn, addr = s.accept()
                self.conn_handler(conn, addr)

        except (socket.error, KeyboardInterrupt):
            s.close()


    def conn_handler(self, conn, addr):
        log.info("Connected by %s" % str(addr))

        try:
            while 1:
                data = conn.recv(1024)
                if not data:
                    break
                self.data_handler(data)

        except (socket.error, KeyboardInterrupt):
            conn.close()
            raise

        conn.close()
