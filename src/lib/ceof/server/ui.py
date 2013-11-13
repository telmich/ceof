# -*- coding: utf-8 -*-
#
# 2012-2013 Nico Schottelius (nico-ceof at schottelius.org)
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
# Generic TCP Server to be used for UI Server
#
#

import ceof
import ceof.config.peer
import ceof.server.tcp
import logging
import socket


log = logging.getLogger(__name__)

class UI(object):
    """Server to accept UI connections"""

    def __init__(self, address, port, config, queue=None):

        self.config = config

        self.tcpserver = ceof.server.tcp.TCPServer(address, port, self.handler)

        self.eofid = ceof.EOFID()
        self.ui_eofid = None

        self.peers = {}

        self.do_exit = False

        self.upstream_queue = queue

    def run(self):
        self.tcpserver.run()

    def handler(self, conn, addr):
        """Handle incoming connection"""

        log.info("UI connected by %s" % str(addr))

        self.conn = conn

        try:
            while not self.do_exit:
                data = conn.recv(ceof.EOF_L_CMD)
                
                # Connection lost
                if not data:
                    break

                cmd = data.decode("utf-8")

                try:
                    log.debug("CMD: " + cmd)
                    fnname = "cmd_" + cmd
                    f = getattr(self, fnname)
                except AttributeError:
                    log.error("Unsupported command: %s" % (cmd))
                    break

                log.debug("Supported command %s" % (cmd))
                f()

        except (socket.error, KeyboardInterrupt):
            conn.close()
            raise

        conn.close()

    def cmd_2100(self):
        """Register UI"""
        
        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))
        self.ui_name = ceof.decode(self.conn.recv(ceof.EOF_L_UI_NAME))

        log.debug("recv id " + self.ui_eofid)
        log.info("Registered UI: %s" % self.ui_name)

        answer = ceof.encode("%s%s" % (ceof.EOF_CMD_UI_ACK, self.ui_eofid))
        self.conn.sendall(answer)

    def cmd_2101(self):
        """De-Register UI"""

        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))

        log.debug("recv id " + self.ui_eofid)
        log.info("De-Registered UI: %s" % self.ui_name)

        # Remove UI
        self.ui_name = ""
        self.conn.close()

    def cmd_2102(self):
        """/peer add"""
        
        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))
        name = ceof.decode(self.conn.recv(ceof.EOF_L_PEERNAME))
        address = ceof.decode(self.conn.recv(ceof.EOF_L_ADDRESS))
        keyid = ceof.decode(self.conn.recv(ceof.EOF_L_KEYID))

        peer_exists = True
        try:
            ceof.Peer.from_disk(self.config.peer_dir, name)
        except ceof.config.peer.NoSuchPeerError:
            peer_exists = False

        if peer_exists:
            answer = (ceof.EOF_CMD_UI_ACK, self.ui_eofid)
            answer_encoded = ceof.encode("%s%s" % answer)
        else:
            answer = (ceof.EOF_CMD_UI_FAIL, self.ui_eofid, "Peer already exists")
            answer_encoded = ceof.encode("%s%s%s" % answer)

        peer = ceof.Peer(name, keyid, [address])
        peer.to_disk(self.config.peer_dir)

        self.conn.sendall(answer_encoded)

    def cmd_2103(self):
        """/peer del"""

        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))
        name = ceof.decode(self.conn.recv(ceof.EOF_L_PEERNAME))

        answer = ceof.encode("%s%s" % (ceof.EOF_CMD_UI_ACK, self.ui_eofid))
        self.conn.sendall(answer)


    def cmd_2104(self):
        """/peer rename"""

        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))
        oldname = ceof.decode(self.conn.recv(ceof.EOF_L_PEERNAME))
        newname = ceof.decode(self.conn.recv(ceof.EOF_L_PEERNAME))

        answer = ceof.encode("%s%s%s%s" % (ceof.EOF_CMD_UI_PEER_RENAMED, self.ui_eofid, 
            ceof.fillup(oldname, ceof.EOF_L_PEERNAME),
            ceof.fillup(newname, ceof.EOF_L_PEERNAME)))
        self.conn.sendall(answer)

    def cmd_2105(self):
        """/peer show"""

        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))
        size = ceof.fillup("2", ceof.EOF_L_SIZE)
        keyid="A35767A98CA9CC3CE368679AB679548202C9B17D"
        addr1=ceof.fillup("tcp://10.2.2.3:4242", 128)
        addr2=ceof.fillup("email://nico-eof42@schottelius.org", 128)

        answer = ceof.encode("%s%s%s%s%s%s" % (ceof.EOF_CMD_UI_PEER_INFO, self.ui_eofid, keyid, size, addr1, addr2))
        self.conn.sendall(answer)

    def cmd_2106(self):
        """/peer list"""

        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))

        peers = ceof.config.peer.Peer.list_peers(self.config.peer_dir)

        size = ceof.fillup(str(len(peers)), ceof.EOF_L_SIZE)
        names=[]
        for peer in peers:
            encoded_name = ceof.fillup(peer.name, ceof.EOF_L_PEERNAME)
            names.append(encoded_name)

        answer = "%s%s%s" % (ceof.EOF_CMD_UI_PEER_LISTING, self.ui_eofid, size)
        answer = answer + "".join(names)
        answer_encoded = ceof.encode(answer)
        self.conn.sendall(answer_encoded)


    def cmd_2107(self):
        """/peer send"""

        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))
        name = ceof.decode(self.conn.recv(ceof.EOF_L_PEERNAME))
        message = ceof.decode(self.conn.recv(ceof.EOF_L_MESSAGE))

        (first_address, onion_chain) = ceof.Onion.create(self.config, name, message)
        self.upstream_queue.put((first_address, onion_chain))

        answer = ceof.encode("%s%s" % (ceof.EOF_CMD_UI_ACK, self.ui_eofid))
        self.conn.sendall(answer)


    def cmd_2199(self):
        """/allquit"""

        self.ui_eofid = ceof.decode(self.conn.recv(ceof.EOF_L_ID))
        answer = ceof.encode("%s%s" % (ceof.EOF_CMD_UI_EXITREQUEST, self.ui_eofid))
        self.do_exit = True
        self.conn.sendall(answer)

