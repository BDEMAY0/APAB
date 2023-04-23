import requests
import ssl
import socket
from pprint import pprint
"""
Le fichier HackWeb.py contient la classe Hack_Web, qui est utilisée pour récupérer les informations sur les bannières des serveurs web. 
Il envoie une requête HEAD aux ports 80 et 443 pour récupérer les en-têtes de réponse HTTP et les affiche ensuite à l'utilisateur.
"""


class Entete:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    # Méthode pour récupérer la bannière du serveur Web
    def get_banner(self):
        # Si le port est 80 (HTTP)
        if self.port == "80":
            response = requests.head(f"http://{self.ip_address}:{self.port}")
            headers = response.headers
            return headers
        # Si le port est 443 (HTTPS)
        if self.port == "443":
            response = requests.head(f"https://{self.ip_address}:{self.port}")
            headers = response.headers
            return f"Bannière du serveur : " + headers.get("Server", "\n") + "Technologie de serveur web : " + headers.get("X-Powered-By", "\n") + "Type de contenu : " + headers.get("Content-Type", "\n")


class TLSSecurityChecker:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def check(self):
        try:
            context = ssl.create_default_context()
            conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.hostname)
            conn.connect((self.hostname, self.port))
            cert = conn.getpeercert()

            print(f"Certificat pour {self.hostname}:")
            pprint(cert)

            protocol_version = conn.version()
            cipher, version, bits = conn.cipher()

            print(f"\nVersion du protocole SSL/TLS: {protocol_version}")
            print(f"Chiffrement utilisé: {cipher}, {bits} bits")

            if protocol_version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
            #Protocole vulnérable
                return True

        except Exception as e:
            return f"Erreur lors de la vérification de la sécurité SSL/TLS pour {self.hostname}: {e}"

