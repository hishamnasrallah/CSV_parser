import paramiko
import os

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
        # os.makedirs(tmp_path, exist_ok=True)
        try:
            self.sftp.get(f"{path}/{file_name}", f"/tmp/{file_name}")
        except:
            x = {"path": path, "tmp_path": tmp_path, "file_name": file_name}
            print(x)


    def read_files_by_prefix_sftp(self, prefix):
        files = []
        for filename in self.sftp.listdir("DcSales"):
            print("file name : ", filename)
            if filename.startswith(prefix):
                with self.sftp.open(filename) as f:
                    # with open(sftp.get("DcSales/"+file_name), 'r') as f:
                    print("file oppened")
                    # print(f.name)
                    file_name = filename
                    files.append(file_name)
                f.close()
        print("here is the  files:   ")
        return files
    def close_connection(self):
        self.client.close()
