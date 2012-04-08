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
    fingerprint=$($ceof -c "$dir" crypto --fingerprint)

    for frompeer in *; do
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
    done

    # And now to the main (my) account
    $ceof peer peer$peer --add --fingerprint "$fingerprint"
    for address in $($ceof -c "$dir" listener -l); do
        echo "Adding to myself $peer frompeer address $address"
            $ceof peer peer$peer --add-address "$address"
    done

done

exit 0

# Create x peers
peers=20

# Create x addresses per peer
addresses=8

port=4235
protobase="tcp://0.0.0.0"

mkdir -p "$peerdir"

i=0
while [ $i -lt $peers ]; do
    echo "Creating peer $i ..."

    dir="$peerdir/$i"

    # Peer missing - generate new key
    if [ ! -d $dir ]; then
        $ceof crypto -c "$dir" --gen-key --name "EOF Peer $i" --email-address "peer$i@example.org"
    fi


    if [ ! "$listener" ]; then
        echo "Adding listener to $dir ..."

        j=1
        while [ $j -le $addresses ]; do
            port=$((port+1))
            j=$((j+1))
            echo Adding ${protobase}:${port}
            $ceof listener -c "$dir" -a ${protobase}:${port}
        done
    fi

    i=$((i+1))
done

