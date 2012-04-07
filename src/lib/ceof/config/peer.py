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
import os
import os.path
import random
import shutil
import sys

log = logging.getLogger(__name__)

class PeerError(ceof.Error):
    pass

class NoSuchPeerError(PeerError):
    pass


@functools.total_ordering
class Peer(object):
    """Handle peer information"""
    
    def __init__(self, name, fingerprint, addresses=[]):
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

    @staticmethod
    def get_peer_dir(base_dir, name):
        """Return peer directory"""

        return os.path.join(base_dir, name)

    @classmethod
    def commandline(cls, args, config):
        """Handle command line arguments"""
        print((args, config))

        if args.remove and args.add:
            raise PeerError("Cannot add and remove a peer at the same time")

        if (args.add or args.remove or args.add_address or args.remove_address) and not args.name:
           raise PeerError("Cannot add/remove/change peer without name")

        if args.add and not args.fingerprint:
            raise PeerError("Cannot add peer without fingerprint")

        # Find peer on disk, if existing
        if args.add or args.remove or args.add_address or args.remove_address:
            directory = cls.get_peer_dir(config.peer_dir, args.name)

            try:
                peer = cls.from_disk(directory)
            except NoSuchPeerError:
                peer = None

        # The actual code part
        if args.add:
            if peer:
                raise PeerError("Peer %s already exists with fingerprint %s" % (peer.name, peer.fingerprint))

            peer = cls(args.name, args.fingerprint)

            if args.add_address:
                for address in args.add_address:
                    peer.add_address(address)

            peer.to_disk(directory)

        elif args.remove:
           # Only remove if existing
            if peer:
                peer.remove_from_disk(config.peer_dir)

        if args.add_address:
            if not peer:
                raise PeerError("Cannot add address to non-existing peer %s" % (args.name))

            for address in args.add_address:
                peer.add_address(address)
            peer.to_disk(directory)

        elif args.remove_address:
            if not peer:
                raise PeerError("Cannot remove address from non-existing peer %s" % (args.name))
            for address in args.remove_address:
                peer.remove_address(address)

            peer.to_disk(directory)

        if args.list:
            for peer in  cls.list_peers(config.peer_dir):
                print(peer)


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

        if not os.path.isdir(directory):
            raise NoSuchPeerError("Peer directory %s does not exist" % directory)

        try:
            with open(name_path, 'r') as f:
                name = f.read().rstrip()

            with open(fingerprint_path, 'r') as f:
                fingerprint = f.read().rstrip()

            with open(addresses_path, 'r') as f:
                addresses = f.read().splitlines()
        except IOError as e:
            raise PeerError("IOError: %s" % e)

        return cls(name, fingerprint, addresses)

    def to_disk(self, directory):
        
        #directory = os.path.join(base_dir, self.name)

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

    def add_address(self, address):
        """Add address to peer"""
        if not address in self.addresses:
            self.addresses.append(address)

    def remove_address(self, address):
        """Remove address from list"""
        if address in self.addresses:
            self.addresses.remove(address)

    def remove_from_disk(self, base_dir):
        """Remove peer from disk"""

        shutil.rmtree(self.get_peer_dir(base_dir, self.name))
