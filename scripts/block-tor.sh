#!/bin/bash
# Block Tor Exit nodes
# Adapted from: https://securityonline.info/block-tor-client-iptablesiptables-tor-transparent-proxy/
IPTABLES_TARGET="DROP"
IPTABLES_CHAINNAME="Tor"
if ! iptables -L Tor -n >/dev/null 2>&1 ; then
  iptables -N Tor >/dev/null 2>&1
  iptables -A OUTPUT -p tcp -j Tor 2>&1
fi
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/../"
iptables -F Tor
CMD=$(cat static-data/tor-node-list.dat | uniq | sort)
for IP in $CMD; do
  if [[ $IP =~ .*:.* ]]
    then
    continue
  fi
  let COUNT=COUNT+1
  iptables -A Tor -d "$IP" -j DROP
done
iptables -A Tor -j RETURN