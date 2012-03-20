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
import gnupg
import logging

log = logging.getLogger(__name__)

class CryptoError(ceof.Error):
    pass

class NoPrivKeyError(CryptoError):
    def __init__(self):
        self.message = "No private/public key pair found (hint: generate a new one)"

    def __str__(self):
        return self.message

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
        self._private_keys = self._gpg.list_keys(True)

    def gen_key(self):
        """Generate new private/public key pair, if none existing"""

        if not self.private_key:
            self._gen_key()
        else:
            raise CryptoError("Private Key already existing")

    def _gen_key(self):
        """Generate new private/public key pair"""

        input_data = self._gpg.gen_key_input(key_type="RSA",
            key_length=self.key_length, name_real=self.name,
            name_comment=self.comment, name_email=self.email)

        log.info("Generating key: (%s)" % input_data)

        self.key = self._gpg.gen_key(input_data)

    @property
    def private_key(self):
        
        # There should only be one private key / we are only
        # interested in the first one
        if not len(self._private_keys) == 0:
            return self._private_keys[0]
        else:
            return None

    def export(self):
        if not self.private_key:
            raise NoPrivKeyError 
            
        # , True = private
        print(self._gpg.export_keys(self.private_key['keyid']))

    def show(self):
        if not self.private_key:
            raise NoPrivKeyError 
            
        print(self.private_key)

# import_result = gpg.import_keys(key_data)
# import_result = gpg.recv_keys('server-name', 'keyid1', 'keyid2', ...)