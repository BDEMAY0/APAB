import json
import requests
from ratelimiter import RateLimiter
import queue
import time

"""
Dans ce fichier, les classes `CVE`, `CVEHandler`, `CVEWorker` et `CVEAnalysis` sont définies 
pour gérer et exécuter l'analyse CVE sur les hôtes et les ports extraits du fichier JSON. 
Les vulnérabilités CVE sont récupérées à l'aide de l'API NVD, et l'analyse est effectuée en parallèle en utilisant des threads 
pour chaque combinaison d'hôte et de port. Enfin, les résultats sont affichés sous forme de chaîne JSON formatée.
"""


class CVE:

    def __init__(self, id, cvss_score):
        self.id = id
        self.cvss_score = cvss_score

    # Méthode pour convertir l'objet CVE en dictionnaire
    def to_dict(self):
        return {"id": self.id, "cvss_score": self.cvss_score}


# Classe pour gérer l'interaction avec l'API NVD et extraire les informations sur les vulnérabilités CVE
class CVEHandler:

    def __init__(self, api_key='80f0cfe4-916f-42e8-84b5-1f6f4ea19262'):
        self.api_key = api_key
        self.headers = {'apiKey': api_key}
        self.rate_limiter = RateLimiter(max_calls=50, period=30)  # 50 requests per 30 seconds

    # Méthode pour obtenir les informations sur les vulnérabilités CVE associées à un CPE spécifique

    def get_cve_info(self, cpe):

        with self.rate_limiter:
            query = f"cpe:2.3:a:{cpe}"
            url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            params = {
                "cpeName": query,
                "resultsPerPage": 50,
            }
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                json_obj = json.loads(response.text)
                return self._extract_cve_info(json_obj)
            else:
                return []


    # Méthode pour extraire les informations pertinentes des vulnérabilités CVE à partir de la réponse de l'API
    def _extract_cve_info(self, response):
        cve_info = []
        for item in response["vulnerabilities"]:
            cve_id = item["cve"]["id"]
            metrics = item["cve"]["metrics"]

            try:
                cvss_v31 = metrics["cvssMetricV31"]
                for metric in cvss_v31:
                    cvss_data = metric["cvssData"]
                    cvss_score = cvss_data["baseScore"]
                    cve_info.append(CVE(cve_id, cvss_score))

            except:
                cvss_v31 = metrics["cvssMetricV2"]
                for metric in cvss_v31:
                    cvss_data = metric["cvssData"]
                    cvss_score = cvss_data["baseScore"]
                    cve_info.append(CVE(cve_id, cvss_score))


        # Trier les vulnérabilités CVE par score CVSS décroissant et ne conserver que les 3 premières
        cve_info.sort(key=lambda x: x.cvss_score, reverse=True)
        return cve_info[:3]


# Classe pour exécuter l'analyse CVE sur un hôte et un port spécifiques en utilisant un thread

class CVEWorker():
    def __init__(self, host, port, cve_handler):
        self.host = host
        self.port = port
        self.cve_handler = cve_handler

    # Méthode exécutée lorsque le thread est lancé
    def run(self):
        if self.port['cpe'] != "N/A":
            cve_info = self.cve_handler.get_cve_info(self.port['cpe'])
            result = {
                "ip": self.host.ip_address,
                "cve_info": [cve.to_dict() for cve in cve_info],
                "product": self.port["product"],
                "version": self.port["version"],
            }
            # Ajoute le résultat dans la file d'attente des résultats
            return result