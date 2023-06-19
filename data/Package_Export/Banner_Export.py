from Package_Export.ManageExport import ManageExport

class Banner_Export(ManageExport):
    def __init__(self, attack_name):
        super().__init__(attack_name)

    def add_banner_host(self, host_ip, port, service, version):
        details = []
        banniere = {}
        banniere["Port"] = port
        banniere["Service"] = service
        banniere["Version"] = version
        details.append(banniere)

        self.hosts.append({
            "ip_address": host_ip,
            "details": details
        })
