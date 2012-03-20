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

import argparse
import curses
import curses.textpad
import socket
import sys
import time


VERSION="0.1"
NAME="ceof"

class CeofUI(object):

    def __init__(self, args):
        self.host = args.connect_to
        self.port = args.port
        self.net = CeofUINet(self.host, self.port)

    def curses_start(self):
        # Begin curse
        self.stdscr = curses.initscr()

        # React on characters without return
        curses.cbreak()

        # Enable cursor support
        self.stdscr.keypad(1)

        self.height, self.width = self.stdscr.getmaxyx()

    def init_windows(self):
        self.window = {}

       # Header data
        self.window["header"] = {}
        self.window["input"] = {}
        self.window["text"] = {}

        self.window["header"]["height"] = 2
        self.window["input"]["height"] = 2
        self.window["text"]["height"] = self.height - \
            self.window["input"]["height"] - self.window["header"]["height"]

        self.window["header"]["window"] = \
            curses.newwin(self.window["header"]["height"], 0, 0 , 0)
        self.window["text"]["window"] = \
            curses.newwin(self.window["text"]["height"], 0, self.window["header"]["height"], 0)
        self.window["input"]["window"] = \
            curses.newwin(self.window["input"]["height"], 0, 
                self.window["text"]["height"] + self.window["header"]["height"], 0)

        # Header: With version and name
        self.window["header"]["window"].insstr(0, 0, NAME + " - " + VERSION)

        # Text: enable scrolling
        self.window["text"]["window"].scrollok(True)
        self.window["text"]["window"].idlok(1)

        # Input: Allow better editing
        self.window["input"]["tb"] = curses.textpad.Textbox(self.window["input"]["window"])

        #self.clean_window("input")
        #self.clean_window("text")

        self.refresh_windows()

    def move_cursor_at_begin(self):
        self.window["input"]["window"].move(1,2)

    def refresh_windows_specific(self, windows):
        """refresh/redraw all windows specified in windows list"""

        for window in windows:
            self.window[window]["window"].refresh()

    def refresh_windows(self):
        # Add bars
        self.window["header"]["window"].insstr(1, 0, self.width * '-')
        self.window["input"]["window"].insstr(0, 0, self.width * '-')

        self.refresh_windows_specific(self.window)

    def clean_window(self, window):
        self.window[window]["window"].erase()
        self.refresh_windows_specific([window])

    def read_line(self):

        line = self.window["input"]["tb"].edit()
        self.clean_window("input")
        return line

        line = []
        while True:
            c = self.window["input"]["window"].getch()

            if c != ord('\n'):
                line.append(chr(c))
            else:
                break

        self.clean_window("input")
        return "".join(line)

    def write_text(self, window, x, y, text):
        """write text to a window"""
        self.window["text"]["window"].addstr(x, y, text)
        self.window["text"]["window"].refresh()

    def write_line(self, line):
        """Write line of text to text window and scroll"""

        lineno = self.window["text"]["height"] - 1
        self.window["text"]["window"].scroll()
        self.refresh_windows()
        self.write_text("text", lineno, 1, line)

    def append_text(self, text):
        """Write text at current position in text window"""

        self.window["text"]["window"].addstr(text)
        self.window["text"]["window"].refresh()

    def curses_stop(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
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

    def main(self):
        self.curses_start()
        self.init_windows()
        self.try_to_connect()

        self.doquit = False
        while not self.doquit:
            self.move_cursor_at_begin()
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


def commandline(argv):
    parser = {}
    
    parser['main'] = argparse.ArgumentParser(description="ceof " + VERSION)
    parser['main'].add_argument('-p', '--port', help='Port to connect to',
        default="4242")
    parser['main'].add_argument('-c', '--connect-to', help='Host to connect to',
        default="127.0.0.1")

    #parser['main'].set_defaults(func=ceof)

    args = parser['main'].parse_args(argv)

    gui = CeofUI(args)

    gui.main()

if __name__ == "__main__":
    try:
        commandline(sys.argv[1:])

    except KeyboardInterrupt:
        pass

    sys.exit(0)



# Old stuff
################################################################################
# Do not display stuff pressed
#curses.noecho()
#win = curses.newwin(height, width, begin_y, begin_x)
#stdscr.border(0)

