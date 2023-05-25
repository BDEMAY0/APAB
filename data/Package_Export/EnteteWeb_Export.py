from Package_Export.ManageExport import ManageExport

class EnteteWeb_Export(ManageExport):
    def __init__(self, attack_name):
        super().__init__(attack_name)

    def add_entete_host(self, host_ip, server, xPoweredBy, xAspNetVersion, accessControlAllowOrigin):
        details = []
        banniere = {}
        banniere["Server"] = server
        banniere["X-Powered-By"] = xPoweredBy
        banniere["X-AspNet-Version"] = xAspNetVersion
        banniere["Access-Control-Allow-Origin"] = accessControlAllowOrigin
        details.append(banniere)

        self.hosts.append({
            "ip_address": host_ip,
            "details": details
        })