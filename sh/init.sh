#!/bin/bash

ENP=$1
ENX=$2

main () {
    echo 1 > /proc/sys/net/ipv4/ip_forward
    iptables -F
    iptables -t nat -F
    iptables -w -t nat -A POSTROUTING -o $ENP -j MASQUERADE
    iptables -A FORWARD -i $ENX -o $ENP -j ACCEPT
    iptables -A FORWARD -i $ENP -o $ENX -m state --state RELATED,ESTABLISHED -j ACCEPT
    iptables -I INPUT -p tcp --dport 6080 -m state --state NEW -j ACCEPT

    return 0
}

main
