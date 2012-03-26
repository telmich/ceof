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

    def curses_start(self):
        # Begin curse
        self.window = curses.initscr()

        # React on characters without return
        curses.cbreak()

        # Enable cursor support
        self.window.keypad(1)
        self.window.idlok(1)

        # Enable scrolling at all
        self.window.scrollok(1)

    def new_window(self, height, offset):
        return curses.newwin(height, 0, offset , 0)

    def init_windows(self):
        self.window = {}

        # Header data
        self.window["header"] = {}
        self.window["input"] = {}
        self.window["text"] = {}


        self.window["header"]["height"] = 2
        self.window["header"]["window"] = \
            self.new_window(self.window["header"]["height"], 0)

        self.window["text"]["height"] = self.height - \
            self.window["input"]["height"] - self.window["header"]["height"]
        self.window["text"]["window"] = \
            curses.newwin(self.window["text"]["height"], 0, self.window["header"]["height"], 0)

        self.window["input"]["height"] = 3
        self.window["input"]["window"] = \
            curses.newwin(self.window["input"]["height"], 0, 
                self.window["text"]["height"] + self.window["header"]["height"], 0)


        #self.window["input"]["window"].border(1, 1, 0, 0, 0, 0, 0, 0)
        #self.window["input"]["window"].border(1, 1, 0, 1, 1, 1, 1, 1)
        # Header: With version and name

        # Text: enable scrolling
        self.window["text"]["window"].scrollok(True)
        #self.window["text"]["window"].idlok(1)

        # Input: Allow better editing
        #self.window["input"]["tb"] = curses.textpad.Textbox(self.window["input"]["window"])

        #self.clean_window("input")
        #self.clean_window("text")

        self.refresh_windows()

    #def refresh_windows_specific(self, windows):
    #    """refresh/redraw all windows specified in windows list"""
#
#        for window in windows:
#            self.window[window]["window"].refresh()

    def refresh_windows(self):
        self.height, self.width = self.window.getmaxyx()
        

        # define scroll region
        self.window.setscrreg(2, self.height-1)

    def orefresh_windows(self):
        # Add bars
        #self.window["header"]["window"].insstr(1, 0, self.width * '-')
        #self.window["input"]["window"].insstr(0, 0, self.width * '-')

        #self.window["text"]["window"].border()
        self.window["header"]["window"].border(1, 1, 1, 0, 1, 1, 0, 0)
        self.window["header"]["window"].insstr(0, 1, "ceof - " + ceof.VERSION)
        #self.window["input"]["window"].border(1, 1, 0, 1, 0, 0, 1, 1)

        self.window["input"]["window"].clear()
        self.window["input"]["window"].border()
        self.window["input"]["window"].insstr(1, 1, "> ")

        self.refresh_windows_specific(self.window)

    def clean_window(self, window):
        return
        self.window.erase()
        self.refresh_windows_specific([window])

    def read_line(self):

        #line = self.window["input"]["tb"].edit()
        #self.clean_window("input")
        #return line

        self.window.move(self.height-1,2)
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

        self.clean_window("input")
        return "".join(line)

    def write_text(self, window, x, y, text):
        """write text to a window"""
        self.window.addstr(x, y, text)
        self.window.refresh()

    def write_line(self, line):
        """Write line of text to text window and scroll"""

        #lineno = self.window["text"]["height"] - 1
        lineno = 2
        self.window.scroll()
        self.refresh_windows()
        self.write_text("text", lineno, 1, line)

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

    def orun(self):
        """ test run """
        self.curses_start()

        #win = curses.newwin(20, 0, 0 , 0)
        self.stdscr.setscrreg(2,20)
        self.stdscr.scrollok(1)
        #self.stdscr.border(0)
        for i in range(2,12):
            self.stdscr.addstr(10,3, "test%d" % (i))
            self.stdscr.scroll()
            self.stdscr.getch()
        #win.setscrreg(1,18)

        #inwin = curses.newwin(3, 0, 13 , 0)



    #cbreak(); noecho(); idlok(stdscr, 1);
    #intrflush(stdscr, FALSE); nodelay(stdscr, TRUE);
    #init_pair(63, 0, 0);
    #resizeterm(term_height, term_width);
    
        self.curses_stop()


    def run(self):
        self.curses_start()
        #self.init_windows()
        self.refresh_windows()
        self.window.insstr(0, 1, "ceof - " + ceof.VERSION)
        self.window.insstr(1, 0, self.width * '-')
        self.refresh_windows()
        #self.try_to_connect()

        self.doquit = False
        while not self.doquit:
            line = self.read_line()

            if line == "/quit" or line == "q":
                break
            else:
                #self.write_text("text", 1, 1, line)
                self.write_line(line)
                print(line)

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

