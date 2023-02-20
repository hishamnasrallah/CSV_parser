import csv
import os
from time import sleep
import paramiko
from app.api.repositories.csv import get_file_history, get_file_mapper, create_file_history, update_last_run
from app.brokers.decapolis_core import CoreApplicationBroker
from utils.sftp_server import SFTPHelper


class CSVHelper:

    def __init__(self, task_id, company_id, file_id, file_name, file_path):
        self.tmp_path = None
        self.file_size = None
        self.file_name_as_received = None
        self.company_id = company_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_id = file_id
        self.task_id = task_id
        self.task_status = None
    # def start_debug_info(self, function_name):
    #     print("@@@@@@@@@@ START working on: ", function_name, " @@@@@@@@@@@@")
    #     print(self.file_size)
    #     print(self.file_name_as_received)
    #     print(self.company_id)
    #     print(self.file_name)
    #     print(self.file_path)
    #     print(self.file_id)
    #     print(self.task_id)
    #
    # def end_debug_info(self, function_name):
    #     print("@@@@@@@@@@ END working on: ", function_name, " @@@@@@@@@@@@")
    #     print(self.file_size)
    #     print(self.file_name_as_received)
    #     print(self.company_id)
    #     print(self.file_name)
    #     print(self.file_path)
    #     print(self.file_id)
    #     print(self.task_id)

    def read_files_by_prefix(self, prefix):
        files = []
        for filename in os.listdir(self.file_path):
            if filename.startswith(prefix):
                with open(os.path.join(self.file_path, filename), 'r') as f:
                    file_name = os.path.basename(f.name)
                    # print(file_name)
                    files.append(file_name)
                f.close()
        new_files = self.is_new_file(files)
        return new_files

    def is_new_file(self, files):
        final_files = []
        for file in files:
            history = get_file_history(file_id=self.file_id, file_name=file)
            if not history.first():
                print(type(files))
                final_files.append(file)

        return final_files

    def get_headers(self):

        mappers = get_file_mapper(self.file_id)
        list_header_fields = []
        for map in mappers:
            # print(map.map_field_name)
            list_header_fields.append(map.map_field_name)
        return list_header_fields

    # def read_file_without_ftp(self, path=None, file_name=None, headers=None):
    #     with open(f"{path}/{file_name}", "r") as file:
    #
    #         keys = headers #file.readline().split(",")
    #         headers = []
    #         for eachKey in keys:
    #             counter = 0
    #             while (eachKey in headers):
    #                 counter += 1
    #                 eachKey = eachKey[:len(eachKey) - (0 if counter == 1 else 1)] + str(counter)
    #             headers.append(eachKey)
    #
    #         mapped_data = []
    #         reader = csv.reader(file, delimiter=',', skipinitialspace=True)
    #         for eachLine in reader:
    #             eachIssue = dict()
    #             columnIndex = 0
    #             for eachColumn in eachLine:
    #                 if columnIndex < len(headers):
    #                     eachIssue[headers[columnIndex]] = eachColumn
    #                     columnIndex += 1
    #             mapped_data.append(eachIssue)
    #         # print(mapped_data)
    #     return mapped_data

    def copy_file_to_tmp_dir(self, file_name):

        client = paramiko.SSHClient()

        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('4.79.195.29', username='decapolis', password='ka%Y5#sGt$')
        sftp = client.open_sftp()
        # sftp.chdir("transfer/napproai")
        print(sftp.getcwd())
        sftp.get(f"transfer/napproai/{file_name}", f"/home/abdallah/csv_files/{file_name}")


    def copy_file_to_tmp_without_sftp(self):
        import shutil
        shutil.copy2(self.file_path+"/"+self.file_name_as_received, self.tmp_path+"/"+self.file_name_as_received)

    def copy_file_to_tmp_sftp(self):
        sftp_helper = SFTPHelper()
        sftp_helper.connect(server_ip='4.79.195.29', username='decapolis', password='ka%Y5#sGt$')
        sftp_helper.change_dir(path="transfer/napproai")
        sftp_helper.copy_file_from_server(path=self.file_path, tmp_path=self.tmp_path, file_name=self.file_name_as_received)

    def remove_temp_file(self, full_file_path):
        os.unlink(full_file_path)

    def read_file(self, path=None, file_name=None, headers=None):

        with open(f"{self.tmp_path}/{file_name}", "r") as file:

            keys = headers #file.readline().split(",")
            headers = []
            for eachKey in keys:
                counter = 0
                while (eachKey in headers):
                    counter += 1
                    eachKey = eachKey[:len(eachKey) - (0 if counter == 1 else 1)] + str(counter)
                headers.append(eachKey)

            mapped_data = []
            reader = csv.reader(file, delimiter=',', skipinitialspace=True)
            for eachLine in reader:
                eachIssue = dict()
                columnIndex = 0
                for eachColumn in eachLine:
                    if columnIndex < len(headers):
                        eachIssue[headers[columnIndex]] = eachColumn
                        columnIndex += 1
                mapped_data.append(eachIssue)
            # print(mapped_data)
        return mapped_data

    def send_data(self, company_id, process_id, data):
        broker = CoreApplicationBroker()
        broker.post_collected_data(company_id=company_id, process_id=process_id, data=data, response_message_key=201)

    def store_history(self):
        create_file_history(self.file_id, self.file_size, self.file_name_as_received, task_id=self.task_id)
        update_last_run(self.file_id)

    def get_tmp_path(self):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sub_folder = "tmp"
        self.tmp_path = os.path.join(current_dir, sub_folder)

    def get_file_info(self):
        # its static now
        # import os
        try:

            size = os.path.getsize(self.tmp_path+"/"+self.file_name_as_received)

        except:
            sleep(secs=5)
            self.get_file_info()

        self.file_size = size
        print(size)

        # with open("/home/hisham/Downloads/headers.csv", 'r') as file:
        #     csvreader = csv.reader(file)
        #     header = next(csvreader)
        #     size = os.path.getsize("/media/hisham/Extreme SSD/mob files/images/Dead sea movenpick-001.zip")
        #     print(size)
        #     print(type(size))
        # return header

    def main(self):
        self.get_tmp_path()
        new_files_names = self.read_files_by_prefix(prefix=self.file_name)
        if not new_files_names:
            self.task_status = "No files"
            return self.task_status
        for file_name in new_files_names:
            self.file_name_as_received = file_name

            self.copy_file_to_tmp_without_sftp()
            #// TODO: use this function copy_file_to_tmp_sftp nestead of copy_file_to_tmp_without_sftp
            data_headers = self.get_headers()

            # self.start_debug_info("copy_file_to_tmp_dir")
            # self.copy_file_to_tmp_dir(file_name)
            # self.end_debug_info("copy_file_to_tmp_dir")

            self.get_file_info()

            mapped_data = self.read_file(path=self.file_path, file_name=file_name, headers=data_headers)

            self.store_history()
            self.remove_temp_file(self.tmp_path+"/"+self.file_name_as_received)
            # self.send_data(self.company_id, process_id, mapped_data)


            return mapped_data

