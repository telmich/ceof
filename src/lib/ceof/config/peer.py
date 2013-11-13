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

class NoPeerAddressError(PeerError):
    pass


@functools.total_ordering
class Peer(object):
    """Handle peer information"""
    
    def __init__(self, name, fingerprint, addresses=[]):
        self.name = name
        self.fingerprint = fingerprint
        self.addresses = addresses
        random.seed()

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

        if args.remove and args.add:
            raise PeerError("Cannot add and remove a peer at the same time")

        if (args.add or args.remove or args.add_address or args.remove_address) and not args.name:
           raise PeerError("Cannot add/remove/change peer without name")

        if args.add and not args.fingerprint:
            raise PeerError("Cannot add peer without fingerprint")

        # Find peer on disk, if existing
        if args.add or args.remove or args.add_address or args.remove_address:
            try:
                peer = cls.from_disk(config.peer_dir, args.name)
            except NoSuchPeerError:
                peer = None

        # The actual code part
        if args.add:
            if peer:
                if not peer.fingerprint == args.fingerprint:
                    raise PeerError("Peer %s already exists with different fingerprint %s" % (peer.name, peer.fingerprint))
            else:
                peer = cls(args.name, args.fingerprint)

            if args.add_address:
                for address in args.add_address:
                    peer.add_address(address)

            peer.to_disk(config.peer_dir)

        elif args.remove:
           # Only remove if existing
            if peer:
                peer.remove_from_disk(config.peer_dir)

        if args.add_address:
            if not peer:
                raise PeerError("Cannot add address to non-existing peer %s" % (args.name))

            for address in args.add_address:
                peer.add_address(address)
            peer.to_disk(config.peer_dir)

        elif args.remove_address:
            if not peer:
                raise PeerError("Cannot remove address from non-existing peer %s" % (args.name))
            for address in args.remove_address:
                peer.remove_address(address)

            peer.to_disk(config.peer_dir)

        if args.list:
            for peer in  cls.list_peers(config.peer_dir):
                print(peer)

    @classmethod
    def random_peer_random_address(cls, base_dir):
        """Return a random address of a random peer"""
        peers = cls.list_random_peers(base_dir, num_peers=1)

        address = peers[0].random_address()

        log.debug("Selected random peer %s with random address %s" % (peers[0], address))
        return address


    @classmethod
    def list_random_peers(cls, base_dir, num_peers, notthispeer=None):
        peers = cls.list_peers(base_dir)
        random_peers = []

        if notthispeer:
            need_peers = num_peers + 1
        else:
            need_peers = num_peers

        if len(peers) < need_peers:
            raise PeerError("Requesting more random peers than available (%s > %s)" % (need_peers, len(peers)))

        for peer_no in range(num_peers):
            peer_index = random.randrange(len(peers))

            peer = peers.pop(peer_index)

            # If the chosen peer is to be avoided, select another one
            if notthispeer:
                if peer == notthispeer:
                    peer_index = random.randrange(len(peers))
                    peer = peers.pop(peer_index)

            random_peers.append(peer)

        log.debug("Random peers:" + str(random_peers))
        return random_peers

    @classmethod
    def list_peers(cls, base_dir):
        peers = []

        for name in os.listdir(base_dir):
            peers.append(cls.from_disk(base_dir, name))

        return peers

    @classmethod
    def from_disk(cls, base_dir, name):
        directory = cls.get_peer_dir(base_dir, name)

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

    def to_disk(self, base_dir):
        directory = self.get_peer_dir(base_dir, self.name)
        
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
        ceof.TransportProtocol.verify_scheme(address)

        if not address in self.addresses:
            self.addresses.append(address)

    def random_address(self):
        """Return random address of peer"""
        num_addr = len(self.addresses)

        # Canot return a random address without at least one peer
        if not num_addr > 0:
            raise NoPeerAddressError

        return self.addresses[random.randrange(num_addr)]

    def list_addresses(self):
        """List address of peer"""
        return self.addresses

    def remove_address(self, address):
        """Remove address from list"""
        if address in self.addresses:
            self.addresses.remove(address)

    def remove_from_disk(self, base_dir):
        """Remove peer from disk"""

        shutil.rmtree(self.get_peer_dir(base_dir, self.name))
