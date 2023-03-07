import paramiko
import os

main_folders = ["napproai", "cecabai"]

class PullFoldersAndFiles:

    def __init__(self):
        self.main_folders = main_folders
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.sftp = None

    def create_main_dir(self):
        for folder in self.main_folders:
            os.makedirs(f'{self.current_dir}/transfer/{folder}', exist_ok=True)

    def connect_to_sftp(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('10.60.22.157', port='2222', username='decapolis', password='ka%Y5#sGt$')
        self.sftp = client.open_sftp()

    def change_dir(self, dir):
        self.sftp.chdir(None)
        self.sftp.chdir(dir)

    def loop_on_folders(self, main_folder, folders):
        for folder in folders:
            self.sftp.chdir(None)
            self.sftp.chdir(f"transfer/{main_folder}/{folder}/")
            files = self.sftp.listdir()
            print(f"{folder}")
            print(files)
            os.makedirs(f'{self.current_dir}/transfer/{main_folder}/{folder}', exist_ok=True)
            sub_folders = []
            for file in files:
                print(file)
                if ".csv" in file or ".man" in file:
                    self.sftp.get(file, f"{self.current_dir}/transfer/{main_folder}/{folder}/{file}")
                else:
                    sub_folders.append(file)
            for sub_folder in sub_folders:
                self.sftp.chdir(None)
                self.sftp.chdir(f"transfer/{main_folder}/{folder}/{sub_folder}")
                os.makedirs(f'{self.current_dir}/transfer/{main_folder}/{folder}/{sub_folder}', exist_ok=True)
                sub_files = self.sftp.listdir()
                new_sub_folders = []

                for file in sub_files:
                    print(file)
                    if ".csv" in file:
                        self.sftp.get(file, f"{self.current_dir}/transfer/{main_folder}/{folder}/{sub_folder}/{file}")
                    else:
                        new_sub_folders.append(file)


    def main(self):
        self.create_main_dir()
        self.connect_to_sftp()

        for main_folder in self.main_folders:
            self.change_dir(f"transfer/{main_folder}/")
            folders = self.sftp.listdir()
            self.loop_on_folders(main_folder, folders)



pull_helper = PullFoldersAndFiles()
pull_helper.main()