import paramiko
import os

class SFTPHelper:

    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None

    def connect(self, server_ip='4.79.195.29', username='decapolis', password='ka%Y5#sGt$'):
    # def connect(self, server_ip='10.60.22.157', port='2222', username='decapolis', password='ka%Y5#sGt$'):
        self.client.connect(server_ip, username=username, password=password)
        # self.client.connect('10.60.22.157', port=2222, username=username, password=password)

        self.sftp = self.client.open_sftp()

    def change_dir(self, path="transfer/napproai"):
        self.sftp.chdir(path)

    def copy_file_from_server(self, path, tmp_path, file_name):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.makedirs(f'{current_dir}/tmp', exist_ok=True)

        try:
            self.sftp.get(f"{file_name}", f"{current_dir}/tmp/{file_name}")
        finally:
            self.close_connection()


    def read_files_by_prefix_sftp(self, prefix):
        files = []
        for filename in self.sftp.listdir():
            if filename.startswith(prefix):
                with self.sftp.open(filename) as f:
                    file_name = filename
                    files.append(file_name)
                f.close()
        return files

    def close_connection(self):
        self.sftp.close()
        self.client.close()
