from Package_Export.ManageExport import ManageExport

class CVE_Export(ManageExport):
    def __init__(self, attack_name):
        super().__init__(attack_name)

    def add_cve_host(self, host_ip, cve_info_list, product, version):
       
        new_details = []
        for cve_info in cve_info_list:
            cve_info["product"] = product
            cve_info["version"] = version
            new_details.append(cve_info)

        # Si l'hote est déjà présent dans l'objet
        for host in self.hosts:
            if host["ip_address"] == host_ip:
                # Si l'host existe alors ajoute les détail à l'ip existante (evite de créer une autre ip similaire dans le json)
                host["details"].extend(new_details)
                return

        self.hosts.append({
            "ip_address": host_ip,
            "details": new_details
        })
