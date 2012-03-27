#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2011 Nico Schottelius (nico-ceof at schottelius.org)
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
import unittest

class IDTestCase(unittest.TestCase):

    def setUp(self):
        self.eofid = ceof.EOFID()

    def test_seed_range(self):
        """Ensure seed is good"""
        self.assertTrue(self.eofid.seed >= 0 and self.eofid.seed <= ceof.EOF_ID_MAX)

    def test_overflow(self):
        """Ensure numbers do not overflow"""
        self.eofid.counter = ceof.EOF_ID_MAX
        self.eofid.inc()

        self.assertEqual(self.eofid.counter, 0)

    def test_convert(self):
        """Test conversions"""

        self.assertEqual(ceof.EOFID.convert_to_id(20), '00000k')
        self.assertEqual(ceof.EOFID.convert_to_id(64), '000010')
        self.assertEqual(ceof.EOFID.convert_to_id(ceof.EOF_ID_MAX), '!!!!!!')

        self.eofid.counter = 63
        self.assertEqual(self.eofid.get_next(), '000010')
