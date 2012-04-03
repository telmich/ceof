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

VERSION     = "0.0.2"

BANNER = """
eof
"""

# /* Lengths */
#EOF_L_RW_SIZE            =  2
EOF_L_VERSION            =  2
EOF_L_CMD                =  4
EOF_L_SIZE               =  6
EOF_L_ID                 =  6
EOF_L_KEYID              =  40
EOF_L_NICKNAME           =  128
EOF_L_MESSAGE            =  128
EOF_L_ADDRESS            =  128
EOF_L_GROUP              =  128
EOF_L_UI_NAME            =  128
EOF_L_UI_INPUT           =  256
EOF_L_MSG_FULL           =  EOF_L_VERSION+EOF_L_CMD+EOF_L_ID+EOF_L_ADDRESS+EOF_L_GROUP+EOF_L_MESSAGE
EOF_L_PKG_MAX            =  65536

# Baseformat for IDs
EOF_ID_CHARS            = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!"
EOF_ID_BASE             = len(EOF_ID_CHARS)
EOF_ID_MAX              = (EOF_ID_BASE**EOF_L_ID)-1

# /* commands */
EOF_CMD_TPS                 = "1000"
EOF_CMD_TPL_START           = "1001"
EOF_CMD_TPL_STOP            = "1002"
EOF_CMD_TPS_START           = "1003"
EOF_CMD_TPS_STOP            = "1004"

EOF_CMD_TPS_DEFAULT         = "20xx"
EOF_CMD_TPS_SENT            = "2000"
EOF_CMD_TPS_NOT_SENT        = "2001"
EOF_CMD_TPL_RECV            = "2002"
EOF_CMD_TPL_LISTENING       = "2003"

# /* user interfaces: already implemented */
EOF_CMD_UI_ACK              = "1100"
EOF_CMD_UI_FAIL             = "1101"
EOF_CMD_UI_EXITREQUEST      = "1102"
EOF_CMD_UI_MSGRECEIVED      = "1103"
EOF_CMD_UI_PEER_LISTING     = "1104"
EOF_CMD_UI_PEER_INFO        = "1105"
EOF_CMD_UI_PEER_RENAMED     = "1106"

EOF_CMD_UI_DEFAULT          = "21xx"
EOF_CMD_UI_REGISTER         = "2100"
EOF_CMD_UI_DEREGISTER       = "2101"
EOF_CMD_UI_PEER_ADD         = "2102"
EOF_CMD_UI_PEER_SEND        = "2103"
EOF_CMD_UI_PEER_RENAME      = "2104"
EOF_CMD_UI_PEER_SHOW        = "2105"
EOF_CMD_UI_PEER_LIST        = "2106"
EOF_CMD_UI_QUIT             = "2199"

# /* crypto engine */
EOF_CMD_CRYPTO_ENCRYPT      = "1200"
EOF_CMD_CRYPTO_DECRYPT      = "1201"

EOF_CMD_CRYPTO_DEFAULT      = "22xx"
EOF_CMD_CRYPTO_ENCRYPTED    = "2200"
EOF_CMD_CRYPTO_DECRYPTED    = "2201"

# /* decoded packets from outside */
EOF_CMD_ONION_DROP          = "3000"
EOF_CMD_ONION_FORWARD       = "3001"
EOF_CMD_ONION_MSG_DROP      = "3002"
EOF_CMD_ONION_MSG_FORWARD   = "3003"
EOF_CMD_ONION_ACK           = "3004"

# /* UI commands */
EOF_UI_EXIT              = "/exit"
EOF_UI_QUIT              = "/quit"
EOF_UI_PEER_ADD          = "/peer add"
EOF_UI_PEER_LIST         = "/peer list"
EOF_UI_PEER_SEND         = "/peer send"
EOF_UI_HELP              = "/help"

# /* environment variables */
EOF_ENV_UI_SOCKET        = "EOF_UI_SOCKET"
EOF_ENV_EOF_HOME         = "EOF_HOME"
EOF_ENV_HOME             = "HOME"

# /* paths */
EOF_P_SLASH              = "/"
EOF_P_CONFIGDIR          = ".ceof"
EOF_P_UI_SOCKET          = EOF_P_SLASH + "ui" + EOF_P_SLASH + "socket"
EOF_P_TP_DIR             = EOF_P_SLASH + "tp"
EOF_P_PIDFILE            = EOF_P_SLASH + "pid"
EOF_P_CRYPTO_DIR         = EOF_P_SLASH + "crypto"
EOF_P_CRYPTO_KEY         = EOF_P_CRYPTO_DIR + EOF_P_SLASH + "mykeyid"

def fillup(data, length):
    """Return string with fill character filled up"""
    return data.ljust(length, '\0')

def encode(data):
    """Encode string for network transfer"""
    return bytes(data, 'utf-8')

def decode(data):
    """Return string without leading zeros"""
    return data.decode('utf-8').rstrip('\0')

class Error(Exception):
    """Base exception class for this project"""
    pass

# Convienence
from ceof.ui.main import Main as UI
from ceof.server.ui import UI as UIServer
from ceof.eofid import EOFID
from ceof.config import Config
from ceof.noise import Noise
#from ceof.crypto import Crypto
