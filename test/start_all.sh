#!/bin/sh -e
# Nico Schottelius, Fri Apr  6 15:43:17 CEST 2012
#
# Add test peers to each other peer

dir=/home/users/nico/privat/bildung/hsz-t/lernen/bachelorarbeit/src
ceof=$dir/bin/ceof
peerdir=$dir/../test/peers

cd $dir
. ./pythonenv 

cd $peerdir

for peer in *; do

    dir="$peerdir/$peer"

    echo $peer ...
    $ceof -c $dir listener --list
    
    $ceof -c $dir server --listener &

    read a
done
