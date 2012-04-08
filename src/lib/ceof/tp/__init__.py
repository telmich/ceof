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

class NoiseQueueEmptyError(ceof.Error):
    def __init__(self):
        self.message = "Noise Queue empty - probably a bug?"

    def __str__(self):
        return self.message

class Transport(object):
    """Transport network packets"""

    def __init__(self, queue, interval, num_peers, noise_dir):

        # Receive real messages from here
        self.message_queue = queue

        # Get fake messages from here
        self._init_noise(noise_dir)

        # Send every interal seconds (1/4 for instance)
        self.interval = interval

        # Have num_peers per route
        self.num_peers = num_peers
        
        self.doexit = False

    def _init_noise(self, noise_dir):
        """Init noise handler"""

        self._noise = ceof.Noise(noise_dir)
        self._noise.start()

    def _get_noise_message(self):
        """Get next noise message"""
        return self._noise.get()

    def route_to(self, peer):
        """Get route to a peer"""
        peers = ceof.Peer.list_random_peers(config.peer_dir, self.num_peers)

        peer_index = random.randrange(len(peers))
        peers.insert(peer)

        return peers

    def create_onion(self, real_peer, ^):
        """Create onion packet"""

        # First peer that receives is the last one to last decrypt
        first_peer = True
        msg=""
        for peer in peers:
            address = peer.get_address(random=True)

            if peer == real_peer:
                if first_peer:
                    cmd = ceof.EOF_CMD_ONION_MSG_DROP
                else:
                    cmd = ceof.EOF_CMD_ONION_MSG_FORWARD
            else:
                if first_peer:
                    cmd = ceof.EOF_CMD_ONION_DROP
                else:
                    cmd = ceof.EOF_CMD_ONION_DROP


                flag |= 
                onion(DROP, eofid.getnext(), addr, group, msg)
                onion(DROP, eofid.getnext(), addr, group, msg)
            else:

    def create_postcard(self, pkg, destination):



    def send(self, text, destination):
        """Send packet from queue"""

        route = self.route_to(destination)

        self.onion(...)?

    def _run(self):
        """Main loop"""

        while not self.doexit:
            # Try to get message, send noise otherwise
            try:
                text, destination = self.message_queue.get(False)
                message = True
            except queue.Empty:
                message = False

            if not message:
                try:
                    text = self.noise_queue.get()
                except queue.Empty:
                    raise NoiseQueueEmptyError

                destination = self.random_recipient()

            self.send(text, destination)
