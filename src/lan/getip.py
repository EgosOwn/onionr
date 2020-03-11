from ipaddress import IPv4Address

from ifaddr import get_adapters

lan_ips = []

for adapter in get_adapters():
    for ip in adapter.ips:
        ip = ip.ip
        try:
            ip = IPv4Address(ip)
            if not ip.is_private or ip.is_loopback:
                raise ValueError
        except ValueError:
            # Raised if not ipv4 or not link local
            continue
        else:
            lan_ips.append(ip.exploded)

