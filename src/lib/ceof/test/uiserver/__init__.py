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

        self.closed = False

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
        """Register close call"""
        self.closed = True
        
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
        self.assertTrue(self.uiserver.conn.closed)

    def test_cmd_2101(self):
        """Emulate 2101 cmd behaviour"""
        eofid = ceof.EOFID().get_next()
        answers = ceof.encode(ceof.EOF_CMD_UI_DEREGISTER + eofid)

        conn = SocketMock(answers)
        self.uiserver.handler(conn, "Fake Connection")
        self.assertTrue(self.uiserver.conn.closed)

    def test_cmd_2102(self):
        """Test /peer add"""

        eofid = ceof.EOFID().get_next()
        nick = ceof.fillup("Testnick", ceof.EOF_L_NICKNAME)
        address = ceof.fillup("tcp:192.168.42.2:22", ceof.EOF_L_ADDRESS)
        keyid = ceof.fillup("A0314E7124560CD3F8885B354918CADD1A6B3063", ceof.EOF_L_KEYID)

        expected_result = ceof.encode(ceof.EOF_CMD_UI_ACK + eofid)
        answers = ceof.encode(ceof.EOF_CMD_UI_PEER_ADD + eofid + nick + address + keyid)

        conn = SocketMock(answers)

        self.uiserver.handler(conn, "Fake Connection")
        self.assertEqual(self.uiserver.conn.sendall_buf, expected_result)
        self.assertFalse(self.uiserver.conn.closed)

    def test_cmd_unknown(self):
        """Send unknown command"""
        eofid = ceof.EOFID().get_next()
        answers = ceof.encode("foo1" + eofid)

        conn = SocketMock(answers)
        self.uiserver.handler(conn, "Fake Connection")
        self.assertTrue(self.uiserver.conn.closed)

