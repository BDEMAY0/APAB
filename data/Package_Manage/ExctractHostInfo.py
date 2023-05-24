import json

class ExctractHostInfo:
    def __init__(self, host):
        try:
            self.ip_address = host["address"][0]["@addr"]
        except:
            self.ip_address = host["address"]["@addr"]
        self.status = host["status"]["@state"]
        self.hostname = host["hostnames"]["hostname"]["@name"] if host.get("hostnames") and host["hostnames"].get("hostname") else "N/A"
        self.ports = self.extract_ports(host)
        self.cve = self.extract_cve(host)

    # Méthode pour extraire les informations sur les ports à partir des données JSON
    @staticmethod

    def extract_ports(host):
        port_info = []
        cpe = ""
        if "ports" in host and "port" in host["ports"]:
            ports = host["ports"]["port"]
            if not isinstance(ports, list):
                ports = [ports]

            for port in ports:
                if "cpe" in port["service"]:
                    cpe_list = port["service"]["cpe"]
                    if not isinstance(cpe_list, list):
                        cpe_list = [cpe_list]
                    cpe = cpe_list[0][7:]  # Prendre seulement la première CPE et supprimer les 5 premiers caractères (cpe:/a:)

                port_data = {
                    'protocol': port['@protocol'],
                    'port_id': port['@portid'],
                    'state': port['state']['@state'],
                    'service_name': port['service']['@name'],
                    'product': port['service'].get('@product', 'N/A'),
                    'version': port['service'].get('@version', 'N/A'),
                    'cpe': cpe if "cpe" in port["service"] else 'N/A',
                }
                port_info.append(port_data)

        return port_info

    # Méthode pour extraire les informations CVE à partir des données JSON
    @staticmethod
    def extract_cve(host):
        cve_list = []

        if "ports" in host and "port" in host["ports"]:
            ports = host["ports"]["port"]
            if not isinstance(ports, list):
                ports = [ports]

            for port in ports:
                if "script" in port:
                    scripts = port["script"]
                    if not isinstance(scripts, list):
                        scripts = [scripts]

                    for script in scripts:
                        if "cve" in script["@id"]:
                            cve_list.append({"id": script["@id"], "output": script["@output"]})


        return cve_list

    # Méthode pour représenter les informations sur l'hôte sous forme de chaîne de caractères
    def __str__(self):
        host_info_str = f"IP Address: {self.ip_address}\n"
        host_info_str += f"Status: {self.status}\n"
        host_info_str += f"Hostname: {self.hostname}\n"
        host_info_str += "Ports:\n"

        for port in self.ports:
            host_info_str += f"  - Protocol: {port['protocol']} | Port ID: {port['port_id']} | State: {port['state']} | Service Name: {port['service_name']} | Product: {port['product']} | Version: {port['version']}\n"

        host_info_str += "CVE:\n"

        for cve in self.cve:
            host_info_str += f"  - ID: {cve['id']} | Output: {cve['output']}\n"

        return host_info_str


    def to_json(self):
        return {
            "host": self.ip_address,
            "hostname": self.hostname,
            "ports": [
                {
                    "protocol": port["protocol"],
                    "port_id": port["port_id"],
                    "service_name": port["service_name"],
                    "product": port["product"],
                    "version": port["version"],
                }
                for port in self.ports
            ],
        }
