import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))

os.makedirs(f'{current_dir}/transfer/napproai', exist_ok=True)
os.makedirs(f'{current_dir}/transfer/cecabai', exist_ok=True)

client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.60.22.157', port='2222', username='decapolis', password='ka%Y5#sGt$')
sftp = client.open_sftp()

sftp.chdir("transfer/cecabai/")
folders = sftp.listdir()
print(folders)
print(sftp.getcwd())
for folder in folders:
    sftp.chdir(None)
    sftp.chdir(f"transfer/cecabai/{folder}/")
    files = sftp.listdir()
    print(f"{folder}")
    print(files)
    os.makedirs(f'{current_dir}/transfer/cecabai/{folder}', exist_ok=True)
    sub_folders = []
    for file in files:
        print(file)
        if ".csv" in file:
            sftp.get(file, f"{current_dir}/transfer/cecabai/{folder}/{file}")
        else:
            sub_folders.append(file)
    for sub_folder in sub_folders:
        sftp.chdir(None)
        sftp.chdir(f"transfer/cecabai/{folder}/{sub_folder}")
        os.makedirs(f'{current_dir}/transfer/cecabai/{folder}/{sub_folder}', exist_ok=True)
        sub_files = sftp.listdir()
        new_sub_folders = []

        for file in sub_files:
            print(file)
            if ".csv" in file:
                sftp.get(file, f"{current_dir}/transfer/cecabai/{folder}/{sub_folder}/{file}")
            else:
                new_sub_folders.append(file)

# sftp.chdir(None)
# sftp.chdir("transfer/napproai/")
# print(sftp.listdir())
# print(sftp.getcwd())
# # transport = client.get_transport()
# # sftp = paramiko.SFTPClient.from_transport(transport)
#
# os.makedirs(f'{current_dir}/tmp', exist_ok=True)
#
# # os.makedirs(f'{current_dir}/tmp')
# remote_file = sftp.open("DcSales/dc_112_sales_20230221093832.csv")
# try:
#     for line in remote_file:
#         print(line)
# finally:
#     remote_file.close()
#
#
# remote_file_path = 'dc_112_sales_20230221093832.csv'
# local_file_path = f'{current_dir}/tmp/dc_112_sales_20230221093832.csv'
# sftp.get(f"DcSales/dc_112_sales_20230221093832.csv", f'{current_dir}/tmp/dc_112_sales_20230221093832.csv')

# with open(local_file_path, 'wb') as f:
#     sftp.get(remote_file_path, f)
# with open("/tmp/dc_112_sales_20230221093832.csv", 'wb') as f:
#     sftp.get(f"dc_112_sales_20230221093832.csv", f)

sftp.close()
# transport.close()
client.close()
# with client.open_sftp() as sftp:
#         sftp.get(f"dc_112_sales_20230221093832.csv", f"/tmp/dc_112_sales_20230221093832.csv")

# def read_files_by_prefix(prefix="dc_"):
#     print("no files yet")
#     files = []
#     for filename in sftp.listdir("DcSales"):
#         print("file name : ", filename)
#         if filename.startswith(prefix):
#             with sftp.open(f"DcSales/"+filename) as f:
#             #with open(sftp.get("DcSales/"+file_name), 'r') as f:
#                 print("file oppened")
#                 #print(f.name)
#                 file_name = filename
#                 files.append(file_name)
#             f.close()
#     print("here is the  files:   " )
#     print(type(files))
#     print(type(files[0]))
#     return files
#    new_files = self.is_new_file(files)
#    return new_files

# print(read_files_by_prefix())


# sftp.get("DcOutboundTransfer/dc_112_obtrans_20230221093952.csv", "dc_112_obtrans_20230221093952.csv")
