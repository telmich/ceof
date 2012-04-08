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
import ceof.tp
import logging
import os
import os.path

log = logging.getLogger(__name__)

class ListenerError(ceof.Error):
    pass

class Listener(object):
    """Load and store ceof listener configuration"""

    def __init__(self, filename):
        self.filename = filename

        if os.path.exists(filename):
            try:
                with open(self.filename, 'r') as f:
                    self.listener = f.read().splitlines()

            except IOError as e:
                raise ListenerError("IOError: %s" % e)

        else:
            self.listener = []
 
    @classmethod
    def commandline(cls, args, config):
        listener = cls(config.listener)

        if args.add:
            for address in args.add:
                listener.add_listener(address)
            listener.to_disk()
        elif args.remove:
            for address in args.remove:
                listener.remove_listener(address)
            listener.to_disk()
        elif args.list:
            for address in listener.list_listener():
                print(address)
    

    def to_disk(self):
        with open(self.filename, 'w') as f:
            listener = '\n'.join(self.listener)
            f.write(listener)

    def add_listener(self, listener):
        """Add listener"""

        if not ceof.TransportProtocol.verify_scheme(listener):
            raise ListenerError("Unknown protocol in address %s" % listener)

        if not listener in self.listener:
            self.listener.append(listener)

    def remove_listener(self, listener):
        """Remove listener"""
        if listener in self.listener:
            self.listener.remove(listener)

    def list_listener(self):
        """Return all registered listener"""
        return self.listener
