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

from ceof.server.listener import Listener

log = logging.getLogger(__name__)


#from ceof.server.listener import Listener

class Server(object):

    def __init__(self):
        pass

    @staticmethod
    def commandline(args, config):
        print(config)
        print(args)
        if args.listener:
            print(config.listener)
            listener = ceof.Listener(config.listener)
            listen_server = Listener(listener.listener)
            listen_server.run()


