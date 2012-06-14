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

class NoiseQueueEmptyError(NoiseError):
    pass

class OnionNoise(object):
    """Create an Onion out of noise"""

    def __init__(self, noise_dir, peer_dir):
        self._noise_dir = noise_dir
        self._peer_dir = peer_dir
        self._noise = Noise(self._noise_dir)

    def get(self, block=True):
        """Get next noise message"""

        try:
            noise_base = self._noise.get(block)
        except queue.Empty:
            raise NoiseQueueEmptyError

        log.debug("Noise: %s" % noise_base)
        eofmsg = ceof.EOFMsg()
        eofmsg.set_message(noise_base)


        # Mimic behaviour of server, which returns address + rest tuple
        return (eofmsg.address, rest)

    def start(self):
        """Start noise generator"""
        self._noise.start()

    def create_noise_onion(self):
        peer = ceof.Peer.random_peer_random_address(self._peer_dir)
        route = ceof.TransportProtocol.route_to(self._peer_dir, peer, ceof.EOF_L_ADDITIONAL_PEERS)
        chain = ceof.TransportProtocol.chain_to(route, peer, message, noise=True)
        onion = cls(gpg_config_dir)
        onion_chain = onion.chain(chain)

        return onion_chain
 

class Server(object):
    """Abstract away noise handling in a subprocess"""

    def __init__(self, noise_dir, block_size = ceof.EOF_L_MSG_FULL):
        self.noise_dir = noise_dir
        self._queue = multiprocessing.Queue()
        self._noise_gen = Generator(self._queue, self.noise_dir, block_size)

    def get(self, block=True):
        """Get next noise message"""
        return self._queue.get(block)

    def start(self):
        """Run child, which provides us with data"""
        try:
            self._process = multiprocessing.Process(target=self._noise_gen.run)
            self._process.start()
        except KeyboardInterrupt:
            log.debug("Caught sigint in server")
            self._queue.close()
            self._queue.cancel_join_thread()

class Generator(object):
    """Generate noise"""

    def __init__(self, queue, noise_dir, block_size):

        # Receive real messages from here
        self.queue = queue

        # Read noise from here
        self._low_level_noise = Filesystem(noise_dir, block_size)

    def run(self):
        """Main loop"""

        try:
            while True:
                log.debug("Adding new noise to the queue")
                block = self._low_level_noise.get_next_block()
                self.queue.put(block)

        except KeyboardInterrupt:
            log.debug("Caught sigint, exiting noise generator")
            self.queue.close()
            self.queue.cancel_join_thread()

class Filesystem(object):
    """Get noise from filesystem"""

    def __init__(self, noise_dir, block_size = ceof.EOF_L_MSG_FULL):
        self.noise_dir = noise_dir

        self._file_handle = False
        self.block_size = block_size

        # Buffer for partial blocks at end of file
        self._file_end_buffer=""

        self._init_files()
        random.seed()

    def _init_files(self):
        """(Re-) Init file list"""
        self._files = os.listdir(self.noise_dir)

        if len(self._files) < 1:
            raise NoiseError("Need at least one file for noise input")

    @classmethod
    def get_direct_noise(cls, noise_dir, block_size):
        """Return noise without server / queue approach"""
        noise = cls(noise_dir, block_size)

        return noise.get_next_block()
        
    def nextfile(self):
        """Return next file to be read for noise input"""
        file_index = random.randrange(0, len(self._files))

        self._filename=os.path.join(self.noise_dir, self._files[file_index])

        log.debug("Next file for reading noise: %s" % self._filename)

        return self._filename

    def get_next_block(self):
        """Return next noise block"""

        block = ""
        # No filehandler? First invocation
        if not self._file_handle:
            self._file_handle = open(self.nextfile(), 'r')

        while not len(block) == self.block_size:
            # File end buffer is large enough
            if len(self._file_end_buffer) >= self.block_size:
                block=self._file_end_buffer[0:self.block_size]
                self._file_end_buffer=self._file_end_buffer[self.block_size:]

            # Read from file as usual
            else:
                try:
                    block = self._file_handle.read(self.block_size)
                except UnicodeDecodeError:
                    # Warn and continue
                    log.warn("Cannot decode to unicode contents of %s" % self._filename)
                    self.nextfile()

            # Not enough bytes in file and file_end_buffer => go to next file
            if len(block) < self.block_size:
                self._file_handle.close()
                self._file_handle = open(self.nextfile(), 'r')
                self._file_end_buffer=self._file_end_buffer + block

        # Eventuelly return block, it's full!
        return(block)
