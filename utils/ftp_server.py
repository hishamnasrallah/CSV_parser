import ftplib
import os

# async
# file_name = "10.60.22.181/csv_files/electronic-card-transactions-december-2022-csv-tables%20%28another%20copy%29.csv"
file_name = "electronic-card-transactions-december-2022-csv-tables.csv"


def ftp_file(file_name=file_name):
    ftp = ftplib.FTP("10.60.22.181")
    ftp.login("abdallah", "fd86grdv9DE8T724dgh")
    ftp.cwd("/csv_files")
    print(ftp.pwd())
    with open(file_name, "wb") as file:
        # ftp.retrbinary("RETR file.txt", file.write)
        # print(file.read())
        keys = ["Series_reference", "Period", "Data_value", "Suppressed", "STATUS", "UNITS", "Magnitude", "Subject", "Series_title_1","Series_title_2", "Series_title_3", "Series_title_4", "Series_title_5"]
        headers = []
        for eachKey in keys:
            counter = 0
            while (eachKey in headers):
                counter += 1
                eachKey = eachKey[:len(eachKey) - (0 if counter == 1 else 1)] + str(counter)
                print(eachKey)
            headers.append(eachKey)
            print(headers)
    ftp.quit()
    return {"message": "File retrieved successfully"}


ftp_file()

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
