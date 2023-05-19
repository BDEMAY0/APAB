import ssl
import socket

class CertificatHTTPS:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def check(self):
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.ip)
            test = conn.connect((self.ip, self.port))
            cert = conn.getpeercert()
            protocol_version = conn.version()
            cipher, version, bits = conn.cipher()
            if protocol_version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
            #Protocole vulnérable
                return protocol_version
            else:
                return ""

        except Exception as e:
            pass
            return ""

