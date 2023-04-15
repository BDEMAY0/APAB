from Package_Attack.Hack_Web import Hack_Web
from Package_Attack.CVE import CVEAnalysis
from Package_Attack.Bruteforce import Bruteforce

"""
 Le fichier Lancheur.py est le fichier principal qui gère l'exécution de tous les modules. 
 Il utilise les modules Hack_Web, Bruteforce, et CVEAnalysis pour effectuer des tâches spécifiques sur les hôtes et 
 les ports extraits du fichier XML. 
"""


# Fonction pour lancer l'attaque par force brute sur le service SSH d'un hôte
def bruteforce_ssh(host, port):
    if port["port_id"] == "22":
        bf = Bruteforce(host.ip_address, 'ressources/ssh/usernames.txt', 'ressources/ssh/passwords.txt')
        result = bf.start()
        print(result)


# Fonction pour lancer l'attaque du serveur Web d'un hôte
def hack_web(host, port):
    if port["port_id"] == "80" or port["port_id"] == "443":
        hw = Hack_Web(host.ip_address, port["port_id"])
        result = hw.get_banner()
        print(result)


# Fonction pour extraire les informations CVE des hôtes à partir du fichier JSON
def exctact_cve(parser):
    #default in object api_key = "80f0cfe4-916f-42e8-84b5-1f6f4ea19262"
    cve_analysis = CVEAnalysis(parser)
    results_by_host = cve_analysis.run_analysis()
    my_cve = cve_analysis.display_results(results_by_host)
    return my_cve
