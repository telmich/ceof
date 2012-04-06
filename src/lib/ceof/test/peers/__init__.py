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
import unittest

class Peers(unittest.TestCase):

    def setUp(self):
        self.num_peers = 8
        self.num_addresses = 8
        self.base_fingerprint = "A35767A98CA9CC3CE368679AB679548202C9B17D"
        self.base_address = "tcp://127.0.0.1:666"
        pass

    def test_read_peers_from_disk(self):
        """Check that all peers from disk are loaded"""
        pass

    def test_write_peers_to_disk(self):
        """Check that all peers in a list are written to disk"""

        peerlist = []
        address_index = 0
        
        for p in range(0, self.num_peers):
            name = "Testpeer%d" % (p)
            fingerprint = self.base_fingerprint[:-1] + str(p)

            for a in range(0, self.num_addresses):
                addresses = self.base_address + str(address_index)
                address_index = address_index + 1

            peerlist.append(ceof.config.Peer(name, fingerprint, addresses))

        print(peerlist)
            
    def test_get_number_of_random_peers(self):
        """From a given list, return a number of random peers"""
        pass


        #random_peers = 

        #self.assertEqual(num_peers, len(random_peers))
