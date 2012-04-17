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
# Generate Noise
#

import ceof
import logging
import multiprocessing
import random
import os
import queue

log = logging.getLogger(__name__)

class NoiseError(ceof.Error):
    pass

class Noise(object):
    """Abstract away noise handling in a subprocess"""

    def __init__(self, noise_dir):
        self.noise_dir = noise_dir
        self._queue = multiprocessing.Queue()
        self._noise_gen = Generator(self._queue, self.noise_dir)

    def get(self, block=True):
        """Get next noise message"""
        return self._queue.get(block)

    def start(self):
        """Run child to provide us with data"""
        try:
            self._process = multiprocessing.Process(target=self._noise_gen.run)
            self._process.start()
        except KeyboardInterrupt:
            log.debug("Caught sigint in parent")
            self._queue.close()
            self._queue.cancel_join_thread()

class Generator(object):
    """Generate noise"""

    def __init__(self, queue, noise_dir):

        # Receive real messages from here
        self.queue = queue

        # Read noise from here
        self.noise_dir = noise_dir

        self.msg_size = ceof.EOF_L_MSG_FULL

        self._init_files()

        random.seed()

    def _init_files(self):
        """(Re-) Init file list"""
        self._files = os.listdir(self.noise_dir)

        if len(self._files) < 1:
            raise NoiseError("Need at least one file for noise input")

    def nextfile(self):
        """Return next file to be read for noise input"""
        file_index = random.randrange(0, len(self._files))

        filename=os.path.join(self.noise_dir, self._files[file_index])

        log.debug("Next file for reading noise: %s" % filename)

        return filename

    def run(self):
        """Main loop"""

        try:
            # everything that is not fitting in a message size is appended here
            file_end_buffer=""
            f = open(self.nextfile(), 'r')

            while True:
                # File end buffer is large enough
                if len(file_end_buffer) >= self.msg_size:
                    msg=file_end_buffer[0:self.msg_size]
                    file_end_buffer=file_end_buffer[self.msg_size:]

                # Read from file as usual
                else:
                    msg = f.read(self.msg_size)

                # Not enough bytes in file and file_end_buffer => go to next file
                if len(msg) < self.msg_size:
                    f.close()
                    f = open(self.nextfile(), 'r')
                    file_end_buffer=file_end_buffer + msg

                # Put noise into queue
                else:
                    self.queue.put(msg)

        except KeyboardInterrupt:
            log.debug("Caught sigint in child")
            self.queue.close()
            self.queue.cancel_join_thread()
