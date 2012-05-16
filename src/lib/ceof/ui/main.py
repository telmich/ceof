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
import ceof.ui.net

import curses
import curses.textpad
import re
import signal
import time

class Main(object):
    """UI class for end user usage"""

    def __init__(self, args):
        #self.host = args.address
        #self.port = args.port
        #self.net = ceof.ui.net.Net(self.host, self.port)
        self.net = ceof.ui.net.Net(args.address, args.port)

        self.prompt = "> "

        self._init_signals()
        self.eofid = ceof.EOFID()

    def _init_signals(self):
        signal.signal(signal.SIGWINCH, self.signal_handler)

    def signal_handler(self, signal, stack):
        self.refresh_windows()
        #self.write_line("Resized")

    def curses_start(self):
        # Begin curse
        self.window = curses.initscr()
        self.stdscr = self.window

        # React on characters without return
        curses.cbreak()

        # Enable cursor support
        self.window.keypad(1)

        # Hardware term support
        self.window.idlok(1)

        # Enable scrolling at all
        self.window.scrollok(1)

    def scroll(self):
        """Scroll up"""
        self.window.scroll()

    def refresh_windows(self):
        """Called on SIGWINCH"""
        self.height, self.width = self.window.getmaxyx()
        curses.resizeterm(self.height, self.width)

        # (Re-)define scroll region
        self.window.setscrreg(2, self.height-2)

        self.draw_title()
        self.window.refresh()

    def prepare_input_line(self):
        """Move cursor to the input line"""

        # Clear input line
        self.window.move(self.height-1,1)
        self.window.clrtoeol()

        # Draw prompt
        self.window.insstr(self.height-1, 1, self.prompt)
        self.window.move(self.height-1, len(self.prompt) + 1)

    def read_line(self):
        """Read and return a line of text"""

        self.prepare_input_line()

        line = []
        while True:
            c = self.window.getch()

            #if c != ord('\n'):
            if c == ord('\n'):
                break
            elif c == curses.KEY_RESIZE:
                continue
            # Read error on SIGWINCH (not documented, but found in reality)
            elif c == -1:
                continue
            else:
                try:
                    line.append(chr(c))
                except ValueError as e:
                    line = "Bad key: %s" % (str(c))
                    break

        return "".join(line)

    def write_text(self, x, y, text):
        """
            Write text to a window

        """
        self.window.addstr(x, y, text)
        self.refresh_windows()

    def write_line(self, line):
        """Write line of text to text window and scroll"""

        # -1 = prompt
        lineno = self.height-2
        self.refresh_windows()

        """First scroll up, then add the text"""
        self.scroll()
        self.write_text(lineno, 1, line)

    def append_text(self, text):
        """Write text at current position in text window"""

        self.window.addstr(text)
        self.window.refresh()

    def curses_stop(self):
        curses.nocbreak()
        self.window.keypad(0)
        curses.echo()
        curses.endwin()

    def connect(self):
        self.write_line("Trying to connect to %s:%s ... " % (self.net.host, self.net.port))
        return self.net.connect()

    def try_to_connect(self):

        for i in range(0,3):
            if self.connect():
                self.write_line("TCP connected to %s:%s" % (self.net.host, self.net.port))
                break
            else:
                self.write_line(str(self.net.error))

        if self.net.connected:
            self.write_line("Attempting logical connection ... ")
            self.eof_connect()
        else:
            self.write_line("Did not manage to connect")
            


    def cmd_connect(self, args):
        """/connect"""
        # Arguments given? Assume different connection, close current!
        if len(args) >= 1:
            self.net.disconnect()
            self.net.host = args[0]

            if len(args) >= 2:
                try:
                    self.net.port = int(args[1])
                except ValueError as ve:
                    self.write_line("/connect: %s: %s" % (args, ve))
                    return

        self.try_to_connect()

    def eof_connect(self):
        """Begin logical connection, register"""

        cmd = "2100"
        eofid = self.eofid.get_next()
        name = ceof.fillup("ceof ui", ceof.EOF_L_UI_NAME)

        data = "%s%s%s" % (cmd, eofid, name)
        self.net.send(ceof.encode(data))

        cmd_answer = ceof.decode(self.net.recv(ceof.EOF_L_CMD))

        # Looks good so far, verify ID
        if cmd_answer == ceof.EOF_CMD_UI_ACK:
            eofid_answer = ceof.decode(self.net.recv(ceof.EOF_L_ID))

            if eofid_answer == eofid:
                self.write_line("Successfully connected")
            else:
                self.write_line("Received wrong ID: %s" % eofid_answer)
        else:
            self.write_line("Did not receive ack: %s" % cmd_answer)


    def cmd_quit(self, args):
        """/quit"""

        cmd = "2101"
        self.net.send(ceof.encode(cmd))
        self.doquit = True

    def cmd_allquit(self, args):
        """/allquit"""

        cmd = "2199"
        eofid = self.eofid.get_next()
        data = "%s%s" % (cmd, eofid)

        self.write_line("Terminating chatserver and all UIs")
        self.net.send(ceof.encode(data))

        #cmd_answer = ceof.decode(self.net.recv(ceof.EOF_L_CMD))
        #cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
        self.write_line("Terminating ourself")
        # Give the user some time to see the message
        time.sleep(1)

        self.doquit = True

    def cmd_peer(self, args):

        # Ignore bad command
        if len(args) == 0:
            self.write_line("Incomplete peer command")
            return

        if args[0] == "add":
            self.cmd_peer_add(args[1:])
        elif args[0] == "del":
            self.cmd_peer_del(args[1:])
        elif args[0] == "rename":
            self.cmd_peer_rename(args[1:])
        elif args[0] == "show":
            self.cmd_peer_show(args[1:])
        else:
            self.write_line("Unsupported peer command: %s" % args[0])

    def cmd_peer_add(self, args):

        if not len(args) == 3:
            self.write_line("/peer add <name> <address> <keyid>")
            return
            
        cmd = ceof.EOF_CMD_UI_PEER_ADD
        eofid = self.eofid.get_next()

        name_plain = args[0]
        name = ceof.fillup(args[0], ceof.EOF_L_PEERNAME)
        address = ceof.fillup(args[1], ceof.EOF_L_ADDRESS)
        keyid = ceof.fillup(args[2], ceof.EOF_L_KEYID)

        data = "%s%s%s%s%s" % (cmd, eofid, name, address, keyid)

        self.net.send(ceof.encode(data))

        cmd_answer = ceof.decode(self.net.recv(ceof.EOF_L_CMD))

        if cmd_answer == ceof.EOF_CMD_UI_ACK:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            self.write_line("Added peer %s" % name_plain)
        elif cmd_answer == ceof.EOF_CMD_UI_FAIL:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            reason = ceof.decode(self.net.recv(ceof.EOF_L_MESSAGE))
            
            self.write_line("Failed to add peer %s: %s" % (name_plain, reason))
        else:
            self.write_line("Unknown response command %s" % cmd_answer)


    def cmd_peer_del(self, args):
        if not len(args) == 1:
            self.write_line("/peer del <name>")
            return
            
        cmd = ceof.EOF_CMD_UI_PEER_DEL
        eofid = self.eofid.get_next()

        name_plain = args[0]
        name = ceof.fillup(args[0], ceof.EOF_L_PEERNAME)

        data = "%s%s%s" % (cmd, eofid, name)

        self.net.send(ceof.encode(data))

        cmd_answer = ceof.decode(self.net.recv(ceof.EOF_L_CMD))

        if cmd_answer == ceof.EOF_CMD_UI_ACK:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            self.write_line("Deleted peer %s" % name_plain)
        elif cmd_answer == ceof.EOF_CMD_UI_FAIL:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            reason = ceof.decode(self.net.recv(ceof.EOF_L_MESSAGE))
            
            self.write_line("Failed to delete peer %s: %s" % (name_plain, reason))
        else:
            self.write_line("Unknown response command %s" % cmd_answer)

    def cmd_peer_rename(self, args):
        if not len(args) == 2:
            self.write_line("/peer rename <oldname> <newname>")
            return
            
        cmd = ceof.EOF_CMD_UI_PEER_RENAME
        eofid = self.eofid.get_next()

        oldname_plain = args[0]
        oldname = ceof.fillup(args[0], ceof.EOF_L_PEERNAME)
        newname_plain = args[1]
        newname = ceof.fillup(args[1], ceof.EOF_L_PEERNAME)

        data = "%s%s%s%s" % (cmd, eofid, oldname, newname)

        self.net.send(ceof.encode(data))

        cmd_answer = ceof.decode(self.net.recv(ceof.EOF_L_CMD))

        if cmd_answer == ceof.EOF_CMD_UI_PEER_RENAMED:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            self.write_line("Renamed peer %s => %s" % (oldname_plain, newname_plain))
        elif cmd_answer == ceof.EOF_CMD_UI_FAIL:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            reason = ceof.decode(self.net.recv(ceof.EOF_L_MESSAGE))
            
            self.write_line("Failed to rename peer %s: %s" % (oldname_plain, reason))
        else:
            self.write_line("Unknown response command %s" % cmd_answer)

    def cmd_peer_show(self, args):
        if not len(args) == 1:
            self.write_line("/peer show <name>")
            return
            
        cmd = ceof.EOF_CMD_UI_PEER_SHOW
        eofid = self.eofid.get_next()

        name_plain = args[0]
        name = ceof.fillup(args[0], ceof.EOF_L_PEERNAME)

        data = "%s%s%s" % (cmd, eofid, name)

        self.net.send(ceof.encode(data))

        cmd_answer = ceof.decode(self.net.recv(ceof.EOF_L_CMD))

        if cmd_answer == ceof.EOF_CMD_UI_PEER_INFO:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            keyid = ceof.decode(self.net.recv(ceof.EOF_L_KEYID))
            num_addresses = ceof.decode(self.net.recv(ceof.EOF_L_SIZE))
            addresses = []

            for num in range(int(num_addresses)):
                addresses.append(ceof.decode(self.net.recv(ceof.EOF_L_ADDRESS)))

            self.write_line("Peer info for %s (%s): %s" % (name_plain, keyid, addresses))
        elif cmd_answer == ceof.EOF_CMD_UI_FAIL:
            cmd_id = ceof.decode(self.net.recv(ceof.EOF_L_ID))
            reason = ceof.decode(self.net.recv(ceof.EOF_L_MESSAGE))
            
            self.write_line("Failed to show peer %s: %s" % (name_plain, reason))
        else:
            self.write_line("Unknown response command %s" % cmd_answer)

    def cmd_peer_send(self, args):
        pass

    def cmd_peer_list(self, args):
        pass

    def cmd_help(self, args):
        """/help"""
        self.write_line("/help:")
        self.write_line("")
        self.write_line("/connect [host] [port] - Connect to chat server")
        self.write_line("/quit - Quit this UI")
        self.write_line("/allquit - Quit this UI, Chatserver and all other UIs")
        self.write_line("/peer add <name> <address> <keyid> - Add peer")
        self.write_line("/peer del <name> - Delete peer")
        self.write_line("/peer send <name> <message> - Send message to peer")
        self.write_line("/peer rename <oldname> <newname> - Rename peer")
        self.write_line("/peer show <name> - Show peer")
        self.write_line("/peer list - List all peers")

    def draw_title(self):
        """(Re-)draw title"""

        self.window.move(0,0)
        self.window.clrtoeol()
        #self.window.insstr(0, 1, "ceof - " + ceof.VERSION)
        self.window.addstr("ceof - " + ceof.VERSION)

        self.window.move(1,0)
        self.window.clrtoeol()
        #self.window.insstr(1, 0, self.width * '-')
        self.window.addstr(self.width * '-')

    def run(self):
        self.curses_start()
        #self.init_windows()
        self.refresh_windows()
        self.try_to_connect()

        self.doquit = False
        while not self.doquit:
            line = self.read_line()
            match = re.search(r"^/(allquit|connect|help|peer|quit)(.*)", line)

            # Commands matching
            if match:
                self.write_line("Found command: %s" % match.group(1))
                fnname = "cmd_" + match.group(1)
                fnargs = match.group(2).split()
                f = getattr(self, fnname)
                f(fnargs)
            # Ignore empty input
            elif line == "":
                continue
            # Send text
            else:
                self.write_line("Unsupported command %s" % line)

        self.curses_stop()
