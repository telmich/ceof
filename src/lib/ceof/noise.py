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

class Server(object):
    """
    Abstract away noise creation in a subprocess
    
    Supports plain noise or encrypted noise generation
    """

    def __init__(self, noise_dir, plain=True, peer_dir="", gpg_config_dir=""):

        if plain:
            self._backend = FilesystemNoise(noise_dir, peer_dir)
        else:
            self._backend = OnionNoise(noise_dir, peer_dir, gpg_config_dir)

        self._queue = multiprocessing.Queue()
        self._noise_gen = Generator(self._queue, self._backend)

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
    """Generate noise (plain or onionised)"""

    def __init__(self, queue, backend):
        # Receive real messages from here
        self.queue = queue

        # Read noise from here
        self._backend = backend

    def run(self):
        """Main loop"""

        try:
            while True:
                log.debug("Adding new noise to the queue")
                block = self._backend.get()
                self.queue.put(block)

        except KeyboardInterrupt:
            log.debug("Caught sigint, exiting noise generator")
            self.queue.close()
            self.queue.cancel_join_thread()

class OnionNoise(object):
    """Create an Onion out of noise"""

    def __init__(self, noise_dir, peer_dir, gpg_config_dir):
        self._noise_dir = noise_dir
        self._peer_dir = peer_dir
        self._onion = ceof.Onion(gpg_config_dir)

    def get(self, block=True):
        """Get next onion that consists of noise only"""

        peer = ceof.Peer.list_random_peers(self._peer_dir, 1)[0]

        route = ceof.TransportProtocol.route_to(self._peer_dir, peer, ceof.EOF_L_ADDITIONAL_PEERS)

        chain = ceof.EOFMsg.chain_noisified(route, peer, message=False, noise_dir=self._noise_dir)

        first_peer = chain[-1]['peer']
        address = first_peer.random_address()

        onion_chain = self._onion.chain(chain)

        return (address, onion_chain)

class FilesystemNoise(object):
    """Create noise including address information"""

    def __init__(self, noise_dir, peer_dir):
        self._noise = Filesystem(noise_dir)
        self._peer_dir = peer_dir

    def get(self, block=True):
        """Get next onion that consists of noise only"""

        peer = ceof.Peer.list_random_peers(self._peer_dir, 1)[0]
        address = peer.random_address()

        noise = self._noise.get()

        return (address, noise)

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

        return noise.get()
        
    def nextfile(self):
        """Return next file to be read for noise input"""
        file_index = random.randrange(0, len(self._files))

        self._filename=os.path.join(self.noise_dir, self._files[file_index])

        log.debug("Next file for reading noise: %s" % self._filename)

        return self._filename

    def get(self):
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
