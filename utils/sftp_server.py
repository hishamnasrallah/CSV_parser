import paramiko


class SFTPHelper:

    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None

    def connect(self, server_ip='4.79.195.29', username='decapolis', password='ka%Y5#sGt$'):
        self.client.connect(server_ip, username=username, password=password)
        self.sftp = self.client.open_sftp()

    def change_dir(self, path="transfer/napproai"):
        self.sftp.chdir(path)

    def copy_file_from_server(self, path, tmp_path, file_name):
        self.sftp.get(f"{path}/{file_name}", f"{tmp_path}/{file_name}")

    def close_connection(self):
        self.client.close()
