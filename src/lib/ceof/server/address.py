# -*- coding: utf-8 -*-
#
# 2013 Nico Schottelius (nico-ceof at schottelius.org)
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

class Adress(object):
    """Sender server"""

    def __init__(self, config, queue=None):
        self._config = config
        self._upstream_queue = queue

    def run(self):
        """Main loop"""

        log.debug("Adress server started")

        continue_running = True

        try:
            while continue_running:
                eofmsg, rest = self._upstream_queue.get(block=True)

                handle_request(eofmsg, rest)

        except KeyboardInterrupt:
            continue_running = False


    def handle_request(self, eofmsg, rest):
        """Dispatch requests to method"""

        cmd = eofmsg.cmd

        if cmd == ceof.EOF_CMD_ONION_ADDR_REG:
            self.queue['address'].put((eofmsg, rest))

        elif cmd == ceof.EOF_CMD_ONION_ADDR_ASK:
            self.queue['address'].put((eofmsg, rest))

        elif cmd == ceof.EOF_CMD_ONION_ADDR_DEREG:
            self.queue['address'].put((eofmsg, rest))
    
        else:
            raise ceof.UnsupportedCommandError(cmd)

