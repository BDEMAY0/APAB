import threading
from Package_Manage.Parser import NmapParser
from Launcher import *

# Le point d'entrée du programme
if __name__ == "__main__":

    with open("data/pentest.txt", "r") as f:
        for line in f:
            key, value = line.strip().split(" :")
            if value == " True":
                globals()[key]()

    # Nom du fichier JSON contenant les résultats de Nmap
    nmap_output_file = "output.json"

    # Création d'un objet NmapParser et chargement du fichier JSON
    parser = NmapParser(nmap_output_file)

    # Extraction des CVEs
    my_cve = exctact_cve(parser)
    print(my_cve)

    # Création de listes pour stocker les threads
    ssh_threads = []
    web_threads = []

    # Itération sur les hôtes et les ports pour lancer les threads de force brute et les attaques web
    for host in parser.host_info_list:
        for port in host.ports:
            # Lancement d'un thread pour la force brute SSH
            t = threading.Thread(target=bruteforce_ssh, args=(host, port))
            t.start()
            ssh_threads.append(t)
            for t in ssh_threads:
                t.join()

            # Lancement d'un thread pour les attaques web
            w = threading.Thread(target=hack_web, args=(host, port))
            w.start()
            ssh_threads.append(w)
            for w in ssh_threads:
                w.join()