import paramiko

class Ssh:
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
            exit(1)

    def send_command(self, command, verbose=True):

        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            if verbose:
                out = stdout.readlines()
                for outs in out:
                    print(outs.split('\n')[0])
        except:
            print("Command execution failed!")
            exit(1)

    def close(self):
        try:
            self.client.close()
        except:
            print("Closing connection failed!")
            exit(1)

    def upload_file(self, local_file, remote_destination):
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_file, remote_destination)
            sftp.close()
        except:
            print("File upload failed!")
            exit(1)

    def download_file(self, remote_file, local_destination):
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_file, local_destination)
            sftp.close()
        except:
            print("File download failed!")
            exit(1)
