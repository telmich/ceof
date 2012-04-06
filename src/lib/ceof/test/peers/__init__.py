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
import ceof.config
import os
import os.path
import shutil
import tempfile
import unittest

class Peers(unittest.TestCase):

    def setUp(self):
        self.num_peers = 8
        self.num_addresses = 8
        self.base_fingerprint = "A35767A98CA9CC3CE368679AB679548202C9B17D"
        self.base_address = "tcp://127.0.0.1:666"

        self.peerlist = []
        address_index = 0
        self.tmpdir = tempfile.mkdtemp()
        self.peer_dir = os.path.join(self.tmpdir, "peers")
        os.mkdir(self.peer_dir)
        
        for p in range(self.num_peers):
            name = "Testpeer%d" % (p)
            fingerprint = self.base_fingerprint[:-1] + str(p)

            for a in range(0, self.num_addresses):
                addresses = self.base_address + str(address_index)
                address_index = address_index + 1

            self.peerlist.append(ceof.config.Peer(name, fingerprint, addresses))

        for peer in self.peerlist:
            peer.to_disk(self.peer_dir)
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_write_peer_to_disk(self):
        """Check that a peer is written to disk"""

        peerdir = os.path.join(self.tmpdir, "testonepeer")
        os.mkdir(peerdir)

        peer = self.peerlist[0]
        peer.to_disk(peerdir)

        files = ['name', 'fingerprint', 'addresses']
        files.sort()

        subdir = os.path.join(peerdir, peer.fingerprint)

        subdir_name = os.listdir(peerdir)[0]
        subdir_content = os.listdir(subdir)
        subdir_content.sort()

        self.assertEqual(subdir_name, peer.fingerprint)
        self.assertEqual(subdir_content, files)

    def test_read_peers_from_disk(self):
        """Check that all peers from disk are loaded"""

        peers = ceof.config.peer.Peer.list_peers(self.peer_dir)
        peers.sort()
        self.peerlist.sort()
        self.assertEqual(peers, self.peerlist)


    def test_get_number_of_random_peers(self):
        """From a given list, return a number of random peers"""

        random_1 = ceof.config.peer.Peer.list_random_peers(self.peer_dir, self.num_peers)
        random_2 = ceof.config.peer.Peer.list_random_peers(self.peer_dir, self.num_peers)

        self.assertNotEqual(random_1, random_2)

        # Remove random and they should be equal, because we selected
        random_1.sort()
        random_2.sort()

        self.assertEqual(random_1, random_2)

    def test_request_too_many_random_peers(self):
        """Select more random peers than available"""

        self.assertRaises(ceof.config.peer.PeerError, 
            ceof.config.peer.Peer.list_random_peers, self.peer_dir, self.num_peers+1)
