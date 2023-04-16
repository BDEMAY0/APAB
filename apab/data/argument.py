import threading
from Package_Manage.Launcher import *


def cve(parser):
    # Extraction des CVEs
    my_cve = l_exctact_cve(parser)
    print(my_cve)


def ssh_bf(parser):
    # Création de listes pour stocker les threads
    ssh_threads = []
    for host in parser.host_info_list:
        for port in host.ports:
            # Lancement d'un thread pour la force brute SSH
            t = threading.Thread(target=l_bruteforce_ssh, args=(host, port))
            t.start()
            ssh_threads.append(t)
            for t in ssh_threads:
                t.join()


def entete_web(parser):
    # Création de listes pour stocker les threads
    web_threads = []
    # Itération sur les hôtes et les ports pour lancer les threads de récupération des entetes web
    for host in parser.host_info_list:
        for port in host.ports:
            # Lancement d'un thread pour les attaques web
            w = threading.Thread(target=l_entete, args=(host, port))
            w.start()
            web_threads.append(w)
            for w in web_threads:
                w.join()


def check_tls(parser):
    for host in parser.host_info_list:
        hostname = host.hostname
        for infoSV in host.ports:
            port = infoSV['port_id']
            if infoSV['service_name'] == 'https':
                tls = l_check_tls(hostname, port)
                return tls