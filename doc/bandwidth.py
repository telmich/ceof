#!/usr/bin/env python3

# size in bytes
pkg_size=4096

# Every x seconds a new packet is sent
interval=0.2

# bit/s
bitrate=(pkg_size*8)/interval


SYMBOLS = ('k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
PREFIX = {}

for i, s in enumerate(SYMBOLS):
    PREFIX[s] = 1 << (i+1)*10

def convert_bytes(n):
    for s in reversed(SYMBOLS):
        if n >= PREFIX[s]:
            value = float(n) / PREFIX[s] 
            return '%.1f %s' % (value, s)

print("Bitrate/s: %s (%s)" % (bitrate, convert_bytes(bitrate/8)))

