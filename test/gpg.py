#!/usr/bin/env python3

import gnupg
import os
import os.path
import shutil

bp="/home/users/nico/hsz-t/lernen/bachelorarbeit/test/gpg"

for i in range(2,11):
    name="peer%d" % (i)
    comment="Test Key for Peer %d" % (i)
    email="peer%d@example.org" % (i)
    path=os.path.join(bp, name)

    print(path)

    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)
    gpg = gnupg.GPG(gnupghome=path)
    input_data = gpg.gen_key_input(key_type="RSA",
        key_length=2048,
        name_real=name,
        name_comment=comment,
        name_email=email)

    print("Generating key (%s)" % input_data)
    key = gpg.gen_key(input_data)

# ascii_armored_public_keys = gpg.export_keys(keyids) # same as gpg.export_keys(keyids, False)
#  ascii_armored_private_keys = gpg.export_keys(keyids, True) # True => private keys

# import_result = gpg.import_keys(key_data)
# import_result = gpg.recv_keys('server-name', 'keyid1', 'keyid2', ...)

