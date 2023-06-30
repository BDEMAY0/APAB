from Package_Export.ManageExport import ManageExport

class Banner_Export(ManageExport):
    def __init__(self, attack_name):
        super().__init__(attack_name)

    def add_banner_host(self, host_ip, port, service, version):
        new_details = []
        banniere = {}
        banniere["Port"] = port
        banniere["Service"] = service
        banniere["Version"] = version
        new_details.append(banniere)

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
