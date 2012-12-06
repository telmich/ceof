#!/bin/sh -e
# Nico Schottelius, Fri Apr  6 15:43:17 CEST 2012
#
# Add test peers to each other peer

if [ $# -ne 2 ]; then
    echo "$0 your-public-ip-address ip-address-of-test-peers"
    exit 1
fi

my_ip=$1; shift
remote_ip=$1; shift

testdir=$(cd ${0%/*} && pwd -P)
peerdir="$testdir/peers"
srcdir=$(cd "$testdir/../src" && pwd -P)
ceof=$srcdir/bin/ceof

cd "$srcdir"
. ./pythonenv 

cd "$peerdir"

lastpeer=5
for peer in $(seq 0 $lastpeer); do

    dir="$peerdir/$peer"
    fingerprint=$($ceof -c "$dir" crypto --fingerprint)

    #for frompeer in *; do
    for frompeer in $(seq 0 $lastpeer); do
        if [ $frompeer = $peer ]; then
            echo "Skipping $peer to itself"
            continue
        fi
        fromdir="$peerdir/$frompeer"
        fromfingerprint=$($ceof -c "$fromdir" crypto --fingerprint)

        echo "Adding $frompeer to $peer ..."
        $ceof -c $dir peer peer$frompeer --add --fingerprint "$fromfingerprint"

        for address in $($ceof -c "$fromdir" listener -l); do
            # Test peers are all running on the same box
            address=$(echo $address | sed 's/0.0.0.0/127.0.0.1/')
            echo "Adding to peer $peer from $frompeer address $address"
            $ceof -c $dir peer peer$frompeer --add-address "$address"
        done

        echo "Importing public key from $frompeer to $peer"
        $ceof -c "$fromdir" crypto --export | $ceof -c $dir crypto --import
    done

    # And now TO the main (my) account
    $ceof peer peer$peer --add --fingerprint "$fingerprint"
    for address in $($ceof -c "$dir" listener -l); do
        address=$(echo $address | sed "s/0.0.0.0/$remote_ip/")
        echo "Adding peer $peer to myself with address $address"
            $ceof peer peer$peer --add-address "$address"
    done

    echo "Importing public key from $peer to myself"
    $ceof -c "$dir" crypto --export | $ceof crypto --import

    # And add my main account to test accounts
    echo "Adding myself to $peer ..."
    fromfingerprint=$($ceof crypto --fingerprint)
    $ceof -c $dir peer nico --add --fingerprint "$fromfingerprint"
    for address in $($ceof listener -l); do
        address=$(echo $address | sed "s/0.0.0.0/$my_ip/")
        echo "Adding myself to peer $peer with address $address"
        $ceof -c $dir peer nico --add-address "$address"
    done

    echo "Importing public key from myself to $peer"
    $ceof crypto --export | $ceof -c $dir crypto --import
done
