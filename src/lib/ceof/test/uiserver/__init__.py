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
import unittest

class SocketMock(object):
    """Mock socket behaviour needed for uiserver testing"""

    def __init__(self, data):
        # Data to be used for answers
        self.recv_buf = data
        self.recv_buf_index = 0

        self.sendall_buf = b''

    def recv(self, length):
        """Return data from pre allocated buffer"""

        newend = self.recv_buf_index + length

        if newend <= len(self.recv_buf):
            begin = self.recv_buf_index
            self.recv_buf_index = newend

            data = self.recv_buf[begin:newend]
        else:
            print("Index: %d, length: %d, readlength: %d" % (self.recv_buf_index, len(self.recv_buf), length))
            data = False

        return data

    def close(self):
        pass
        
    def sendall(self, data):
        """Return data the client wanted to send"""
        self.sendall_buf = self.sendall_buf + data

    def __str__(self):
        return str({ 'recv': self.recv_buf,
                 'sendall': self.sendall_buf })

class UIServer(unittest.TestCase):

    def setUp(self):
        self.uiserver = ceof.UIServer("127.0.0.1", "9993")

    def test_cmd_2100(self):
        """Emulate 2100 cmd behaviour"""
        eofid = ceof.EOFID().get_next()
        uiname = ceof.fillup("Mockui", ceof.EOF_L_UI_NAME)
        #print(eofid)
        answers = ceof.encode(ceof.EOF_CMD_UI_REGISTER + eofid + uiname)
        #print(answers)
        expected_result = ceof.encode(ceof.EOF_CMD_UI_ACK + eofid)
        #print(expected_result)

        conn = SocketMock(answers)

        #print(self.uiserver.conn)

        # Run cmd_2100
        self.uiserver.handler(conn, "Fake Connection")

        self.assertEqual(self.uiserver.conn.sendall_buf, expected_result)

#    def test_overflow(self):
#        """Ensure numbers do not overflow"""
#        self.eofid.counter = ceof.EOF_ID_MAX
#        self.eofid.inc()
#        self.assertEqual(self.eofid.counter, 0)
#
#    def test_getnext_id(self):
#        """Test that get_next returns correct id"""
#
#        self.eofid.counter = 63
#        self.assertEqual(self.eofid.get_next(), '000010')
#
#    def test_convert_to_id(self):
#        """Test conversions (int => id)"""
#
#        self.assertEqual(ceof.EOFID.int_to_id(20), '00000k')
#        self.assertEqual(ceof.EOFID.int_to_id(64), '000010')
#        self.assertEqual(ceof.EOFID.int_to_id(ceof.EOF_ID_MAX), '!!!!!!')
#
#    def test_convert_to_int(self):
#        """Test conversions (id => int)"""
#
#        self.assertEqual(ceof.EOFID.id_to_int('00000k'), 20)
#        self.assertEqual(ceof.EOFID.id_to_int('000010'), 64)
#        self.assertEqual(ceof.EOFID.id_to_int('!!!!!!'), ceof.EOF_ID_MAX)
