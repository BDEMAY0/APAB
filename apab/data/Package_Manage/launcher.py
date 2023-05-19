from Package_Attack.EnteteWeb import EnteteWeb
from Package_Attack.CVE import CVEWorker
from Package_Attack.CVE import CVEHandler
from Package_Attack.Bruteforce import Bruteforce_ssh
from Package_Attack.MacFlooding import MacFlooding
from Package_Attack.DhcpStarvation import DhcpStarvation
from Package_Export.CVE_Export import CVE_Export
from Package_Export.ManageExport import ManageExport
from Package_Export.EnteteWeb_Export import EnteteWeb_Export
from Package_Attack.SMBScanner import SMBScanner
from Package_Attack.STPAttack import STPAttack
from Package_Attack.CertificatHTTPS import CertificatHTTPS
import threading



"""
 Le fichier lancheur.py est le fichier principal qui gère l'exécution de tous les modules. 
Toutes ces fonctions sont appelés dans le main.py et sont appelés selon le choix de l'utilisateur (après avoir cocher les checkboxs)
"""


"""
Si vous souhaitez ajouter votre propre attaque, vous devez ajouter votre fonction avec le même nommage qui sera dans le fichier texte après avoir cocher l'attaque par l'utilisateur
Ensuite vous pouvez ajouter votre module dans Package_Attack. 
Puis si vous voulez personnalisé votr export --> Creer votre module dans Package_Export. 
"""

#Interface réseau de la raspberry qui va être utilisé.
interface = "eth0"


###############################################################
#                      ATTAQUES SYSTEMES                      #
###############################################################

# Fonction pour lancer l'attaque par force brute sur le service SSH d'un hôte
def ssh_bf(parser):
    result_by_host = []

    #Sous fonction permettant de faire du multithreading sur cette attaque. 
    def thread_bruteforce_ssh(host, port):
        if port["port_id"] == "22" or port["service_name"] == "ssh":
            bf = Bruteforce_ssh(host.ip_address, 'ressources/ssh/usernames.txt', 'ressources/ssh/passwords.txt')
            hote, username  = bf.start()
            result_by_host.append((hote, username))

    def export_ssh():
        ssh_report = ManageExport("Bruteforce SSH")
        has_password_ssh = False  # Variable pour vérifier si des informations cve_info sont présentes

        for result in result_by_host:
            ip_address, username = result
            if username:
                # Si cve_info est présent pour un hôte, on met à jour le statut de la vulnérabilité à True
                ssh_report.success = True  
            
            ssh_report.add_host(ip_address, username)

    # Création de listes pour stocker les threads
    ssh_threads = []
    for host in parser.host_info_list:
        for port in host.ports:
            # Lancement d'un thread pour la bf SSH
            t = threading.Thread(target=thread_bruteforce_ssh, args=(host, port))
            t.start()
            ssh_threads.append(t)
            for t in ssh_threads:
                t.join()
    #Appel de la sous fonction d'export pour le json
    export_ssh()


#Fonction pour extraire les informations CVE des hôtes à partir du fichier JSON
def cve(parser):
    result_by_host = []
    
    def l_cve(host, port, cve_handler):   # Création de listes pour stocker les threads
        mon_hote = CVEWorker(host, port, cve_handler)
        result_hote = mon_hote.run()
        result_by_host.append(result_hote)

    def export_cve():
        cve_report = CVE_Export("CVE")
        cve_info = []
        host_ip = ""
        product = ""
        version = ""
        for result in result_by_host:
            try:
                host_ip = result.get('ip')
                cve_info = result.get('cve_info')
                product = result.get('product')
                version = result.get('version')
            except:
                pass

            if cve_info:
                # Si cve_info est présent pour un hôte, on met à jour le statut de la vulnérabilité à True
                cve_report.success = True  
            
            cve_report.add_cve_host(host_ip, cve_info, product, version)
    #Avoir la meme instance pour l'objet CVEHandler afin de limiter les connexions à l'API avec la bibl Ratelimiter
    cve_handler = CVEHandler()
    ssh_threads = []
    for host in parser.host_info_list:
        for port in host.ports:
            # Lancement d'un thread pour la bf SSH
            t = threading.Thread(target=l_cve, args=(host, port, cve_handler))
            t.start()
            ssh_threads.append(t)
            for t in ssh_threads:
                t.join()
    export_cve()
   

# Fonction pour lancer l'attaque du serveur Web d'un hôte
def entete_web(parser):
    result_by_host = []
     #Sous fonction permettant de faire du multithreading sur cette attaque. 
    def thread_entete(host, port):
        if port["port_id"] == "80" or port["port_id"] == "443" or port["service_name"] == "http" or port["service_name"] == "https":
            #récup de l'entete
            mon_objet = EnteteWeb(host.ip_address, port["port_id"])
            ip, server, xPoweredBy, xAspNetVersion, accessControlAllowOrigin = mon_objet.get_banner()
            result_by_host.append((ip, server, xPoweredBy, xAspNetVersion, accessControlAllowOrigin))

    def export_entete():
        entete_report = EnteteWeb_Export("Entete Web")
        for result in result_by_host:
            ip, server, xPoweredBy, xAspNetVersion, accessControlAllowOrigin = result
            if server or xPoweredBy or xAspNetVersion or accessControlAllowOrigin :
                # Si cve_info est présent pour un hôte, on met à jour le statut de la vulnérabilité à True
                entete_report.success = True  
            
            entete_report.add_entete_host(ip, server, xPoweredBy, xAspNetVersion, accessControlAllowOrigin)

    # Création de listes pour stocker les threads
    web_threads = []
    # Itération sur les hôtes et les ports pour lancer les threads de récupération des entetes web
    for host in parser.host_info_list:
        for port in host.ports:
            # Lancement d'un thread pour les attaques web
            w = threading.Thread(target=thread_entete, args=(host, port))
            w.start()
            web_threads.append(w)
            for w in web_threads:
                w.join()
    export_entete()


 # Fonction pour lancer l'attaque pour check le protocole du certificat
def check_tls(parser):
    result_by_host = []

    def export_tls():
        tls_report = ManageExport("TLS")
        for result in result_by_host:
            ip_address, protocole = result
            if protocole:
                # Si cve_info est présent pour un hôte, on met à jour le statut de la vulnérabilité à True
                tls_report.success = True  
            
            tls_report.add_host(ip_address, protocole)  

    for host in parser.host_info_list:
        for infoSV in host.ports:
            port = infoSV['port_id']
            if infoSV['service_name'] == 'https' or infoSV["port_id"] == "443":
                tls = CertificatHTTPS(host.ip_address, int(port))
                protocole = tls.check()
                result_by_host.append((host.ip_address, protocole))
    export_tls()  

#Fonction permettant de savoir si des dossiers sont ouverts en tant qu'anonyme
def smb_scanner(parser):
    for host in parser.host_info_list:
        for port in host.ports:
            if port["port_id"] == "445":
                smb = SMBScanner(host.ip_address)
                attack_success = smb.manager()  

    
###############################################################
#                      ATTAQUES RESEAUX                       #
###############################################################
    
def mac_flooding(parser):
    #Fonction pour lancer l'attaque de flooding MAC sur les commutateurs
    num_packets = 1000 # Nombre de paquets de MAC flooding à envoyer
    num_threads = 100 # Nombre de threads à utiliser pour envoyer les paquets

    mac_flooding = MacFlooding(interface, num_packets, num_threads)
    attack_succes = mac_flooding.run()
    
    
def dhcp_starvation(parser):
    #Fonction pour lancer l'attaque de DHCP starvation sur les serveurs DHCP
    num_requests = 10000 # Nombre de demandes DHCP à envoyer
    num_threads = 100 # Nombre de threads à utiliser pour envoyer les demandes DHCP
    dhcp_starvation = DhcpStarvation(interface, num_requests, num_threads)
    dhcp_starvation.run_attack()
    attack_succes = dhcp_starvation.check_dhcp_failure(timeout=10)
  
        
def stp_attack(parser):
    attack = STPAttack(interface=interface, num_packets=1000, priority=0)
    attack_succes = attack.run()
    

###############################################################
#                      PARTIE AUDIT                       #
###############################################################


# Fonction permettant de savoir toutes les informations de mal configuration sur la partie audit = port HTTP/NETBIOS/BANNIERE SERVICE/
def audit(parser):    
    test=""
    #Sous fonction permettant de savoir si un service http est ouvert
    def web_vuln(host):
        
        for port in host.ports:
            if port["port_id"] == "80" or port["service_name"] == "http":
                test = "HTTP Vulnerability", f"Host: {host.ip_address} Port: {port['port_id']}", True, ""

    #Sous fonction permettant de savoir si un service netbios est ouvert
    def netbios_vuln(host):
        for port in host.ports:
            if port["port_id"] == "139" or port["service_name"] == "netbios-ssn":
                test = "NetBIOS Vulnerability", f"Host: {host.ip_address} Port: {port['port_id']}", True, ""
    
    #Sous fonction permettant de savoir si un service dispose de sa banniere
    def banner_vuln(host):
        for port in host.ports:
            if port["version"] != "N/A":
                test = "Banner Vulnerability", f"Host: {host.ip_address} Port: {port['port_id']}", True, f"""Voici la bannière du service : {port["version"]}"""

    for host in parser.host_info_list:
        web_vuln(host)
        netbios_vuln(host)
        banner_vuln(host)

        
        
           
         







