from Package_Export.ManageExport import ManageExport

class Wifi_Export(ManageExport):
    def __init__(self, attack_name):
        super().__init__(attack_name)

    def add_ap_info(self, ssid, crypto):
        
        self.hosts.append({
            "SSID": ssid,
            "Crypto": crypto
        })