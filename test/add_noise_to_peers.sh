#!/bin/sh -e
# Nico Schottelius, Tue Apr 17 22:14:43 CEST 2012
#
# Add noise to test peers to each other peer

dir=/home/users/nico/privat/bildung/hsz-t/lernen/bachelorarbeit/src
ceof=$dir/bin/ceof
peerdir=$dir/../test/peers

rfc_dir=~/oeffentlich/rechner/netz/rfc/mirror/rfcs-text-only

cd $dir
. ./pythonenv 

cd $peerdir

for peer in *; do
    dir="$peerdir/$peer/noise"

    find $rfc_dir -type f -maxdepth 1 -exec ln -s {} $dir \;
done
