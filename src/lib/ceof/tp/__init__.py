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
import os.path
import re

log = logging.getLogger(__name__)

class TransportProtocolError(ceof.Error):
    pass

class TransportProtocol(object):
    """Common transport helper"""

    def __init__(self):
        pass

    @classmethod
    def commandline(cls, args, config):
        if args.list:
            for protocol in cls.list_protocols():
                print(protocol)

    @staticmethod
    def list_protocols():
        protocols = []
        filename = "__init__.py"
        base_dir = os.path.dirname(os.path.realpath(__file__))

        for possible_protocol in os.listdir(base_dir):
            mod_path = os.path.join(base_dir, possible_protocol, filename)

            if os.path.isfile(mod_path):
                protocols.append(possible_protocol)

        return protocols
     
    @classmethod
    def verify_scheme(cls, address):
        """Verify given address if the scheme (=protocol) is available"""
        protocols = cls.list_protocols()

        match = re.match("(.*?)://", address)
        if not match:
            return False

        protocol = match.group(1)

        return protocol in protocols
