#!/bin/bash

ENP=$1
ENX=$2

main () {
    is_up=$(ip link ls up | grep $ENX)
    echo "Checking interface $ENX is up"
    if [ "$is_up" = "" ]
    then
        echo "Setting up interface $ENX"
        ip addr del 192.168.137.1/24 dev $ENX
        ip addr add 192.168.137.1/24 dev $ENX
        ip link set $ENX up
        echo "nameserver 10.10.0.1" | tee /etc/resolv.conf
        systemctl restart dnsmasq.service
        iptables -D FORWARD 2
        iptables -D FORWARD 1
        iptables -A FORWARD -i $ENX -o $ENP -j ACCEPT
        iptables -A FORWARD -i $ENP -o $ENX -m state --state RELATED,ESTABLISHED -j ACCEPT
    fi
    echo "Interface $ENX is up"
    return 0
}

main
