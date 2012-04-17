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

#for peer in *; do
for peer in $(seq 0 2); do

    dir="$peerdir/$peer"
    fingerprint=$($ceof -c "$dir" crypto --fingerprint)

    #for frompeer in *; do
    for frompeer in $(seq 0 2); do
        if [ $frompeer = $peer ]; then
            echo "Skipping $peer to itself"
            continue
        fi
        fromdir="$peerdir/$frompeer"
        fromfingerprint=$($ceof -c "$fromdir" crypto --fingerprint)

        echo "Adding $frompeer to $peer ..."
        $ceof -c $dir peer peer$frompeer --add --fingerprint "$fromfingerprint"

        for address in $($ceof -c "$fromdir" listener -l); do
            echo "Adding to peer $peer from $frompeer address $address"
            $ceof -c $dir peer peer$frompeer --add-address "$address"
        done

        echo "Importing public key from $frompeer to $peer"
        $ceof -c "$fromdir" crypto --export | $ceof -c $dir crypto --import
    done

    # And now TO the main (my) account
    $ceof peer peer$peer --add --fingerprint "$fingerprint"
    for address in $($ceof -c "$dir" listener -l); do
        echo "Adding $peer to myself with address $address"
            $ceof peer peer$peer --add-address "$address"
    done

    echo "Importing public key from $peer to myself"
    $ceof -c "$dir" crypto --export | $ceof crypto --import

    # And add my main account to test accounts
    echo "Adding myself to $peer ..."
    fromfingerprint=$($ceof crypto --fingerprint)
    $ceof -c $dir peer nico --add --fingerprint "$fromfingerprint"
    for address in $($ceof listener -l); do
        echo "Adding myself to peer $peer with address $address"
        $ceof -c $dir peer nico --add-address "$address"
    done

    echo "Importing public key from myself to $peer"
    $ceof crypto --export | $ceof -c $dir crypto --import
done
