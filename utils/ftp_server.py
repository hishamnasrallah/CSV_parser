import ftplib
import os

# file_name = "10.60.22.181/csv_files/electronic-card-transactions-december-2022-csv-tables%20%28another%20copy%29.csv"
file_name = "electronic-card-transactions-december-2022-csv-tables.csv"


def ftp_file(file_name=file_name):
    ftp = ftplib.FTP("10.60.22.181")
    ftp.login("abdallah", "fd86grdv9DE8T724dgh")
    ftp.cwd("/csv_files")
    with open(file_name, "wb") as file:
        keys = ["Series_reference", "Period", "Data_value", "Suppressed", "STATUS", "UNITS", "Magnitude", "Subject", "Series_title_1","Series_title_2", "Series_title_3", "Series_title_4", "Series_title_5"]
        headers = []
        for eachKey in keys:
            counter = 0
            while (eachKey in headers):
                counter += 1
                eachKey = eachKey[:len(eachKey) - (0 if counter == 1 else 1)] + str(counter)
            headers.append(eachKey)
    ftp.quit()
    return {"message": "File retrieved successfully"}


ftp_file()
