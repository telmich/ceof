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
import tempfile
import unittest

class Address(unittest.TestCase):

    def setUp(self):
        pass

    def test_address_list(self):
        """Ensure that address listing returns all addresses"""
        addresses = ["tcp://192.168.23.24:8080",
            "mailto://a@example.org", "http://example.net:4242/eof" ]

        s_addresses = sorted(addresses)

        with tempfile.TemporaryDirectory() as tempdir:
            for address in addresses:
                addr = ceof.Address(address)
                addr.to_disk(base_dir=tempdir)

            found_addresses = ceof.Address.list_addresses(base_dir=tempdir)
            s_found_addresses = sorted(found_addresses)

            self.assertEqual(s_addresses, s_found_addresses)
