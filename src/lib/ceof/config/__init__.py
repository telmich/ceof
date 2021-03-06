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
#

import ceof
import logging
import os

log = logging.getLogger(__name__)

# /* paths */ - FIXME: probably obsolete
#EOF_P_PIDFILE            = EOF_P_SLASH + "pid"

class ConfigError(ceof.Error):
    pass

class Config(object):
    """Load and store ceof configuration"""

    def __init__(self, config_dir):
        self._init_config_dir(config_dir)
        self._verify_config_dir()
        self._create_directories()

    def _init_config_dir(self, config_dir):
        """Find/setup configuration config_dir"""
        # Prefer what the user said
        if config_dir:
            self.config_dir = config_dir
        else:
            if 'HOME' in os.environ:
                self.config_dir = os.path.join(os.environ['HOME'], '.ceof')
            else:
                self.config_dir = None

    def _verify_config_dir(self):
        """Verify configuration directory option"""
        if not self.config_dir:
            raise ConfigError("Cannot find configuration directory")

    def _create_directories(self):
        """Create required configuration directories"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.gpg_config_dir, exist_ok=True)
        os.makedirs(self.noise_dir, exist_ok=True)
        os.makedirs(self.peer_dir, exist_ok=True)

    @property
    def gpg_config_dir(self):
        return os.path.join(self.config_dir, "gnupg")

    @property
    def listener(self):
        return os.path.join(self.config_dir, "listener")

    @property
    def noise_dir(self):
        return os.path.join(self.config_dir, "noise")

    @property
    def peer_dir(self):
        return os.path.join(self.config_dir, "peer")

