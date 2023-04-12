import json

class NmapParser:
    def __init__(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            self.hosts = data["nmaprun"]["host"]
            self.host_info_list = []

            for host in self.hosts:
                host_info = HostInfo(host)
                self.host_info_list.append(host_info)

    def __str__(self):
        return "\n=====================================\n".join(str(host_info) for host_info in self.host_info_list)

class HostInfo:
    def __init__(self, host):
        try:
            self.ip_address = host["address"][0]["@addr"]
        except:
            self.ip_address = host["address"]["@addr"]
        self.status = host["status"]["@state"]
        self.hostname = host["hostnames"]["hostname"]["@name"] if host.get("hostnames") and host["hostnames"].get("hostname") else "N/A"
        self.ports = self.extract_ports(host)
        self.cve = self.extract_cve(host)

    @staticmethod
    def extract_ports(host):
        port_info = []

        if "ports" in host and "port" in host["ports"]:
            ports = host["ports"]["port"]
            if not isinstance(ports, list):
                ports = [ports]

            for port in ports:
                port_data = {
                    'protocol': port['@protocol'],
                    'port_id': port['@portid'],
                    'state': port['state']['@state'],
                    'service_name': port['service']['@name'],
                    'product': port['service'].get('@product', 'N/A'),
                    'version': port['service'].get('@version', 'N/A'),
                }
                port_info.append(port_data)

        return port_info

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

if __name__ == "__main__":
    nmap_output_file = "output.json"
    parser = NmapParser(nmap_output_file)
    print(parser)
    commande = "rm options.txt"
    subprocess.run(commande, shell=True, stdout=subprocess.PIPE)