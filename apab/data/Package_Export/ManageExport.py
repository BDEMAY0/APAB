import json
import os 

class ManageExport:
    all_attacks = []

    def __init__(self, attack_name):
        self.attack_name = attack_name
        self.hosts = []
        self.success = False
        ManageExport.all_attacks.append(self)

    def add_host(self, host_ip, details=None):
        self.hosts.append({
            "ip_address": host_ip,
            "details": details or []
        })

    @classmethod
    def export_all_to_json(cls, filename):
        attacks_json = []
        for attack in cls.all_attacks:
            attack_json = {
                "attack_name": attack.attack_name,
                "success": attack.success,
                "hosts": attack.hosts,
            }
            attacks_json.append(attack_json)

        directory = "data/ressources/rapport"
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)

        with open(filepath, "w") as file:
            json.dump(attacks_json, file, indent=2)