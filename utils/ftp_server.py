import ftplib
import os

async def ftp_file(file_path, file_name):
    ftp = ftplib.FTP("10.60.22.181")
    ftp.login("abdullah", "fd86grdv9DE8T724dgh")
    ftp.cwd("/csv_files")
    with open("file.txt", "wb") as file:
        ftp.retrbinary("RETR file.txt", file.write)
    ftp.quit()
    return {"message": "File retrieved successfully"}


    # def read_files_by_prefix1(self, prefix):
    #     files = []
    #     for filename in os.listdir(self.file_path):
    #         if filename.startswith(prefix):
    #             with open(os.path.join(self.file_path, filename), 'r') as f:
    #                 file_name = os.path.basename(f.name)
    #                 # print(file_name)
    #                 files.append(file_name)
    #             f.close()
    #     new_files = self.is_new_file(files)
    #     return new_files
