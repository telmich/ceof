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
        """Called on SIGWINCH?"""
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

    def cmd_connect(self, args):
        """/connect"""
        self.write_line(str(args))

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
        if self.net.connected:
            self.eof_connect()

    def eof_connect(self):
        """Begin logical connection, register"""

        cmd = "2100"
        eofid = self.eofid.get_next()
        data = "%s%s" % (cmd, eofid)
        self.net.send(bytes(data, 'utf-8'))

    def cmd_quit(self, args):
        """/quit"""
        self.doquit = True

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
        #self.try_to_connect()

        self.doquit = False
        while not self.doquit:
            line = self.read_line()
            match = re.search(r"^/(connect|quit)(.*)", line)

            # Commands matching
            if match:
                self.write_line(match.group(1))
                fnname = "cmd_" + match.group(1)
                fnargs = match.group(2).split()
                f = getattr(self, fnname)
                f(fnargs)
            # Ignore empty input
            elif line == "":
                continue
            # Send text
            else:
                self.write_line(line)

        self.curses_stop()
