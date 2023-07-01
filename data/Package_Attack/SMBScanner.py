import subprocess

class SMBScanner:
    def __init__(self, ip):
        self.ip = ip
        self.total_return = []

    def racine_folders(self):
        folders = []
        command = f"smbclient -L {self.ip} -N"
        try:
            output = subprocess.check_output(command, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            return []

        for line in output.splitlines():
            if "Disk" in line:
                share = line.split()[0]
                if share not in ['NETLOGON', 'SYSVOL', 'print$']:
                    folders.append(share)

        return folders

    def check_anonymous_access(self, path):
        folders = []
        command = f"smbclient //{self.ip}/{path} -N -c 'ls'"
        try:
            output = subprocess.check_output(command, shell=True).decode("utf-8")
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    directory = parts[1]
                    if "D" in directory:
                        folder = parts[0]
                        if folder not in ['.', '..']:
                            sub_path = folder
                            folders.append(sub_path)
                            new_command = f"smbclient //{self.ip}/{path} -N -c 'cd {sub_path}; ls'"
                            new_output = subprocess.check_output(new_command, shell=True).decode("utf-8")
                            for new_line in new_output.splitlines():
                                new_parts = new_line.split()
                                if len(new_parts) >= 2:
                                    new_directory = new_parts[1]
                                    if "D" in new_directory:
                                        new_folder = new_parts[0]
                                        if new_folder not in ['.', '..']:
                                            new_sub_path = sub_path + '/' + new_folder
                                            folders.append(new_sub_path)
        except subprocess.CalledProcessError as e:
            pass
        return folders

    def manager(self):
        shares = self.racine_folders()
        for share in shares:
            sub_folders = self.check_anonymous_access(share)
            self.total_return.append(share)
            self.total_return.extend(sub_folders)

        state = True if self.total_return else False
        return state, self.total_return
