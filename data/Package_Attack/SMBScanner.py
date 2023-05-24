import subprocess

class SMBScanner:
    def __init__(self, ip):
        self.ip = ip
        self.total_return = []

    def racine_folders(self):
        folders = []
        command = f"smbclient -L {self.ip} -N"
        output = subprocess.check_output(command, shell=True).decode("utf-8")

        for line in output.splitlines():
            if "Disk" in line:
                share = line.split()[0]
                if share not in ['NETLOGON', 'SYSVOL']:
                    folders.append(share)

        return folders

    def check_anonymous_access(self, path):
        racine = False
        folders = []
        command = f"smbclient //{self.ip}/{path} -N -c 'ls'"
        try:
            output = subprocess.check_output(command, shell=True).decode("utf-8")
            racine = True
            for line in output.splitlines():
                directory = line.split()[1]
                if "D" in directory and "DR" not in directory and "DHR" not in directory:
                    folder = line.split()[0]
                    if folder not in ['.', '..']:
                        sub_path = path + '/' + folder
                        folders.append(sub_path)

        except:
            pass
        return racine, folders

    def recursive_check(self, folder):
        has_access, folders = self.check_anonymous_access(folder)
        if has_access:
            for sub_folder in folders:
                self.total_return.append(sub_folder)
                self.recursive_check(sub_folder)

    def manager(self):
        state = False
        shares = self.racine_folders()
        for share in shares:
            has_access, folders = self.check_anonymous_access(share)
            if has_access:
                state = True
                self.total_return.append(share)
                for sub_folder in folders:
                    self.total_return.append(sub_folder)
                    self.recursive_check(sub_folder)
        return state, self.total_return