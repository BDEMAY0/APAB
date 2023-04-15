import requests

"""
Le fichier HackWeb.py contient la classe Hack_Web, qui est utilisée pour récupérer les informations sur les bannières des serveurs web. 
Il envoie une requête HEAD aux ports 80 et 443 pour récupérer les en-têtes de réponse HTTP et les affiche ensuite à l'utilisateur.
"""


class Hack_Web:
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

