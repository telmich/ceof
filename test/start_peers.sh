#!/bin/sh -ex
# Nico Schottelius, Fri Apr  6 15:43:17 CEST 2012
#
# Add test peers to each other peer

testdir=$(cd ${0%/*} && pwd -P)
peerdir="$testdir/peers"
srcdir=$(cd "$testdir/../src" && pwd -P)
ceof=$srcdir/bin/ceof

cd "$srcdir"
. ./pythonenv 

cd $peerdir
for peer in $(seq 0 5); do

    dir="$peerdir/$peer"

    echo $peer ...
    $ceof -c $dir listener --list
    
    $ceof -c $dir server -d --no-noise &
done
