import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
"""
Le fichier Entete.py contient la classe EnteteWeb, qui est utilisée pour récupérer les informations sur les bannières des serveurs web. 
Il envoie une requête HEAD aux ports 80 et 443 pour récupérer les en-têtes de réponse HTTP et les affiche ensuite à l'utilisateur.
"""


class EnteteWeb:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    # Méthode pour récupérer la bannière du serveur Web
    def get_banner(self):
        server = ""
        powered = ""
        aspnet = ""
        acao = ""
        try:
            scheme = "https" if self.port == "443" else "http"
            response = requests.head(f"{scheme}://{self.ip_address}:{self.port}", verify=False)
            headers = response.headers

            # Vérification des en-têtes
            if "Server" in headers:
                server = headers['Server']
            if "X-Powered-By" in headers:
                powered = headers['X-Powered-By']
            if "X-AspNet-Version" in headers:
                aspnet = headers['X-AspNet-Version']
            if "Access-Control-Allow-Origin" in headers and headers['Access-Control-Allow-Origin'] == '*':
                acao = headers['Access-Control-Allow-Origin']
        except: 
            pass

        return self.ip_address, server, powered, aspnet, acao