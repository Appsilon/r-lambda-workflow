import paramiko
import scp

class ssh:
    client = None

    def __init__(self, ip, key_path):

        try:
            cert = paramiko.RSAKey.from_private_key_file(key_path)
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("connecting...")
            self.client.connect(hostname=ip, username="ec2-user", pkey=cert)
            print("connected!!!")


        except:
            print("Connection Failed!!!")

    def send_command(self, command):

        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            print(stdout.readlines())
        except:
            print("Command execution failed!")

    def close(self):
        try:
            self.client.close()
        except:
            print("Closing connection failed!")