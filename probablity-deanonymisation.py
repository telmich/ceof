#!/usr/bin/env python3

import sys

def n_choose_r(n, r):
    result = 1
    for j in range(1, r+1):
        result = result * ((n + 1 - j) / j)
        
    return result

if not len(sys.argv) == 3:
    print("%s: route_peers network_peers" % sys.argv[0])
    sys.exit(1)

proxy_peers=int(sys.argv[1])
network_peers=int(sys.argv[2])

print("%s aus %s" % (proxy_peers, network_peers))

factor_1 = 1
for j in range(proxy_peers):
    factor_2 = network_peers - j

    result = factor_1 * factor_2
    print("%s * %s = %s" % (factor_1, factor_2, result))

    factor_1 = result

left_side = result

factor_1 = 1
for j in range(1, proxy_peers+1):
    factor_2 = j

    result = factor_1 * factor_2
    print("%s * %s = %s" % (factor_1, factor_2, result))

    factor_1 = result

right_side = result

print("Probability (%s of %s): 1:%d" % (proxy_peers, network_peers, left_side/right_side))
