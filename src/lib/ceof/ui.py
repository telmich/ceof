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
import curses
import curses.textpad
import socket
import sys
import time


class UI(object):
    """UI class for end user usage"""

    def __init__(self, args):
        self.host = args.address
        self.port = args.port
        self.net = CeofUINet(self.host, self.port)

        self.prompt = "> "

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
            #elif c == curses.KEY_BACKSPACE:
            #    line.append("B")
            else:
                line.append(chr(c))

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
        self.write_line("Trying to connect to %s:%s ... " % (self.host, self.port))
        return self.net.connect()

    def try_to_connect(self):

        for i in range(0,3):
            if self.connect():
                break
            else:
                self.append_text(str(self.net.error))

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

            if line == "/quit" or line == "q":
                break
            # Ignore empty input
            elif line == "":
                continue
            else:
                self.write_line(line)

        self.curses_stop()


class CeofUINet(object):
    """
    This class handles the network connection to the chat server
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        try:
            self.socket = socket.create_connection((self.host, self.port))
        except socket.error as e:
            self.connected = False
            self.error = e
        else:
            self.connected = True

        return self.connected

        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.connect((self.host, int(self.port)))

# Old stuff
#    def orun(self):
#        """ test run -- works"""
#        self.curses_start()
#
#        #win = curses.newwin(20, 0, 0 , 0)
#        self.stdscr.setscrreg(2,20)
#        self.stdscr.scrollok(1)
#        #self.stdscr.border(0)
#        for i in range(2,12):
#            self.stdscr.addstr(10,3, "test%d" % (i))
#            self.stdscr.scroll()
#            self.stdscr.move(30,2)
#            self.stdscr.getch()
#        #win.setscrreg(1,18)
#
#        #inwin = curses.newwin(3, 0, 13 , 0)
#    
#        self.curses_stop()


