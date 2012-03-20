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

import gnupg
import logging

log = logging.getLogger("ceof.crypto")

class Crypto(object):
    """Manage cryptographic functions"""

    def __init__(self, config, name="Your Friendly Name", 
        email="you@example.org", comment="EOF42KEY", key_length=2048):

        self.config = config
        self.name = name
        self.email = email
        self.key_length = key_length
        self.comment = comment

        self._gpg = gnupg.GPG(gnupghome=config.gpg_config_dir)

    def gen_key(self):
        """Generate new private/public key pair"""

        input_data = self._gpg.gen_key_input(key_type="RSA",
            key_length=self.key_length, name_real=self.name,
            name_comment=self.comment, name_email=self.email)

        log.info("Generating key: (%s)" % input_data)

        self.key = self._gpg.gen_key(input_data)

# ascii_armored_public_keys = gpg.export_keys(keyids) # same as gpg.export_keys(keyids, False)
#  ascii_armored_private_keys = gpg.export_keys(keyids, True) # True => private keys

# import_result = gpg.import_keys(key_data)
# import_result = gpg.recv_keys('server-name', 'keyid1', 'keyid2', ...)

