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
import functools
import logging
import random
import os

log = logging.getLogger(__name__)

class PeerError(ceof.Error):
    pass

@functools.total_ordering
class Peer(object):
    """Handle peer information"""
    
    def __init__(self, name, fingerprint, addresses):
        self.name = name
        self.fingerprint = fingerprint
        self.addresses = addresses

    def __str__(self):
        return "%s/%s/%s" % (self.name, self.fingerprint, str(self.addresses))

    def __repr__(self):
        return "<%s/%s>" % (self.name, self.fingerprint)

    def __eq__(self, other):
        return ((self.name, self.fingerprint) == (other.name, other.fingerprint))

    def __lt__(self, other):
        return ((self.name, self.fingerprint) < (other.name, other.fingerprint))

    def address_add(self, address):
        self.addresses.append(address)

    @staticmethod
    def writepeers(base_dir, listofpeers):
        pass

    @classmethod
    def list_random_peers(cls, base_dir, num_peers):
        peers = cls.list_peers(base_dir)
        random_peers = []
        random.seed()

        if len(peers) < num_peers:
            raise PeerError("Requesting more random peers than available (%s > %s)" % (num_peers, len(peers)))

        for peer in range(num_peers):
            peer_index = random.randrange(len(peers))
            peer = peers.pop(peer_index)

            random_peers.append(peer)

        return random_peers

    @classmethod
    def list_peers(cls, base_dir):
        peers = []

        for peerdirname in os.listdir(base_dir):
            peerdir = os.path.join(base_dir, peerdirname)
            
            peers.append(cls.from_disk(peerdir))

        return peers

    @classmethod
    def from_disk(cls, directory):
        name_path = os.path.join(directory, "name")
        fingerprint_path = os.path.join(directory, "fingerprint")
        addresses_path = os.path.join(directory, "addresses")

        with open(name_path, 'r') as f:
            name = f.read().rstrip()

        with open(fingerprint_path, 'r') as f:
            fingerprint = f.read().rstrip()

        with open(addresses_path, 'r') as f:
            addresses = f.read().splitlines()

        return cls(name, fingerprint, addresses)

    def to_disk(self, base_dir):
        
        directory = os.path.join(base_dir, self.fingerprint)

        if os.path.exists(directory):
            if not os.path.isdir(directory):
                raise ceof.config.ConfigError("%s exist but is not a directory" % directory)
        else:
            os.mkdir(directory)

        name_path = os.path.join(directory, "name")
        fingerprint_path = os.path.join(directory, "fingerprint")
        addresses_path = os.path.join(directory, "addresses")

        with open(name_path, 'w') as f:
            f.write(self.name)

        with open(fingerprint_path, 'w') as f:
            f.write(self.fingerprint)

        with open(addresses_path, 'w') as f:
            addresses = '\n'.join(self.addresses)
            f.write(addresses)

    def address_add(self, address):
        """Add address to list"""
        self.addresses.append(address)

    def address_replace(self, address):
        """Replace address list with new address"""
        self.addresses = [address]


    def delete(self, name):
        pass