from Package_Export.ManageExport import ManageExport

class CVE_Export(ManageExport):
    def __init__(self, attack_name):
        super().__init__(attack_name)

    def add_cve_host(self, host_ip, cve_info_list, product, version):
        details = []
        for cve_info in cve_info_list:
            cve_info["product"] = product
            cve_info["version"] = version
            details.append(cve_info)

        self.hosts.append({
            "ip_address": host_ip,
            "details": details
        })