import json
from Package_Manage.ExctractHostInfo import ExctractHostInfo

"""
Le fichier NmapParser.py contient la classe NmapParser qui est utilisée pour extraire les informations d'hôte et de port du fichier JSON fourni. 
Les objets HostInfo sont créés pour chaque hôte avec les informations pertinentes et stockés dans une liste. 
La classe HostInfo extrait les informations sur les ports et les vulnérabilités CVE à partir des données JSON. 
"""


class NmapParser:
    def __init__(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            self.hosts = data["nmaprun"]["host"]
            self.host_info_list = []

            for host in self.hosts:
                host_info = ExctractHostInfo(host)
                self.host_info_list.append(host_info)

    def __str__(self):
        return "\n=====================================\n".join(str(host_info) for host_info in self.host_info_list)

    def get_ip_addresses(self):
        return [host_info.ip_address for host_info in self.host_info_list]

    def save_to_json(self, output_file_path):
        data = {}
        for host_info in self.host_info_list:
            host_json = host_info.to_json()
            data[host_json["host"]] = host_json
            del data[host_json["host"]]["host"]

        with open(output_file_path, "w") as file:
            json.dump(data, file, indent=2)

