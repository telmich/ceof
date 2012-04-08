#!/bin/sh -e
# Nico Schottelius, Fri Apr  6 15:43:17 CEST 2012

dir=/home/users/nico/privat/bildung/hsz-t/lernen/bachelorarbeit/src
ceof=$dir/bin/ceof
peerdir=$dir/../test/peers

cd $dir
. ./pythonenv 

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

    listener=$($ceof -c "$dir" listener -l)

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

