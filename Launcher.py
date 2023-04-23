from Package_Attack.Hack_Web import Entete
from Package_Attack.Hack_Web import TLSSecurityChecker
from Package_Attack.CVE import CVEAnalysis
from Package_Attack.Bruteforce import Bruteforce_ssh
from Package_Attack.MacFlooding import MacFlooding

"""
 Le fichier Lancheur.py est le fichier principal qui gère l'exécution de tous les modules. 
 Il utilise les modules Hack_Web, Bruteforce, et CVEAnalysis pour effectuer des tâches spécifiques sur les hôtes et 
 les ports extraits du fichier XML. 
"""


# Fonction pour lancer l'attaque par force brute sur le service SSH d'un hôte
def l_bruteforce_ssh(host, port):
    if port["port_id"] == "22":
        bf = Bruteforce_ssh(host.ip_address, '../ressources/ssh/usernames.txt', 'ressources/ssh/passwords.txt')
        bf_status = bf.start()
        return bf_status


# Fonction pour lancer l'attaque du serveur Web d'un hôte
def l_entete(host, port):
    if port["port_id"] == "80" or port["port_id"] == "443":
        #récup de l'entete
        hw = Entete(host.ip_address, port["port_id"])
        entete = hw.get_banner()
        return entete


# Fonction pour extraire les informations CVE des hôtes à partir du fichier JSON
def l_exctact_cve(parser):
    #default in object api_key = "80f0cfe4-916f-42e8-84b5-1f6f4ea19262"
    cve_analysis = CVEAnalysis(parser)
    results_by_host = cve_analysis.run_analysis()
    my_cve = cve_analysis.display_results(results_by_host)
    return my_cve


def l_check_tls(hostname, ports):
    # Fonction pour lancer l'attaque pour check le protocole du certificat
    tls = TLSSecurityChecker(hostname, ports)
    return tls
    
    
def l_mac_flooding():
    #Fonction pour lancer l'attaque de flooding MAC sur les commutateurs
    interface = "eth0" # Remplacer eth0 par l'interface réseau sur laquelle vous voulez effectuer l'attaque
    num_packets = 1000 # Nombre de paquets de MAC flooding à envoyer
    num_threads = 100 # Nombre de threads à utiliser pour envoyer les paquets

    mac_flooding = MacFlooding(interface, num_packets, num_threads)
    mac_flooding.run()