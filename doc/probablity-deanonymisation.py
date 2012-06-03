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

# print("%s aus %s" % (proxy_peers, network_peers))

def calc_probability(proxy_peers, network_peers):
    factor_1 = 1
    for j in range(proxy_peers):
        factor_2 = network_peers - j

        result = factor_1 * factor_2
        # print("%s * %s = %s" % (factor_1, factor_2, result))

        factor_1 = result

    left_side = result

    factor_1 = 1
    for j in range(1, proxy_peers+1):
        factor_2 = j

        result = factor_1 * factor_2
        # print("%s * %s = %s" % (factor_1, factor_2, result))

        factor_1 = result

    right_side = result
    probability = left_side/right_side

    return probability

print("De-Anon one packet:\n")
for network_peers in (10**1, 10**2, 10**3, 10**4, 10**5):
    result_list = []
    for proxy_peers in range(1, 8+1):
        probability = calc_probability(proxy_peers, network_peers)
        #result_list.append(str(probability))
        result_list.append("%g" % probability)

    print("\\hline\n\\textbf{%s} & %s\\\\" % (network_peers, " & ".join(result_list)))

print("De-Anon one packet:\n")

for proxy_peers in range(1, 10+1):
    result_list = []
    for network_peers in (10**1, 10**2, 10**3, 10**4, 10**5):
        probability = calc_probability(proxy_peers, network_peers)
        #result_list.append(str(probability))
        result_list.append("1:%g" % probability)

    print("\\hline\n\\textbf{%s} & %s\\\\" % (proxy_peers, " & ".join(result_list)))

print("Average Latency/Number of proxies:\n")

for proxy_peers in range(1, 10+1):
    avg_delay = 0
    for j in range(1, proxy_peers+1):
        avg_delay = avg_delay + j
        
    avg_delay = avg_delay / (proxy_peers+1)

    times = []
    header = []
    for interval in (1/8, 1/4, 1/2, 1, 2):
        header.append("%ss" % interval)
        times.append("%gs" % (interval * avg_delay))

    print("\\hline\n\\textbf{%s} & %g & %s\\\\" % (proxy_peers, avg_delay, " & ".join(times)))



print("Maximum Latency/Number of proxies:\n")

for proxy_peers in range(1, 10+1):
    max_delay = proxy_peers

    times = []
    header = []
    for interval in (1/8, 1/4, 1/2, 1, 2):
        header.append("%ss" % interval)
        times.append("%gs" % (interval * max_delay))

    print("\\hline\n\\textbf{%s} & %g & %s\\\\" % (proxy_peers, max_delay, " & ".join(times)))


print("Bandwidth usage\n")

pkg_sizes = [1.2, 1.9, 2.6, 3.3, 4.0, 4.8, 5.6, 6.3, 7.1, 8.0]
for proxy_peers in range(1, 10+1):

    bandwidth = []
    for interval in (1/8, 1/4, 1/2, 1, 2):
        bandwidth.append("%g" % (pkg_sizes[proxy_peers-1] * (1/interval)))

    print("\\hline\n\\textbf{%s} & %s\\\\" % (proxy_peers, " & ".join(bandwidth)))


