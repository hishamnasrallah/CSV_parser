import csv
import os

from app.api.repositories.csv import get_file_history, get_file_mapper, create_file_history, update_last_run
from app.brokers.decapolis_core import CoreApplicationBroker


class CSVHelper:

    def __init__(self, task_id, company_id, file_id, file_name, file_path):
        self.file_size = None
        self.file_name_as_received = None
        self.company_id = company_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_id = file_id
        self.task_id = task_id

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
        for file in files:
            history = get_file_history(file_id=self.file_id, file_name=file)
            if history.first():
                print(type(files))
                files.remove(file)

        return files

    def get_headers(self):

        mappers = get_file_mapper(self.file_id)
        list_header_fields = []
        for map in mappers:
            # print(map.map_field_name)
            list_header_fields.append(map.map_field_name)
        return list_header_fields

    def read_file(self, path=None, file_name=None, headers=None):
        with open(f"{path}/{file_name}", "r") as file:

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


    def get_file_info(self):
        # its static now
        import os
        size = os.path.getsize(self.file_path)
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
        new_files_names = self.read_files_by_prefix(prefix=self.file_name)
        for file_name in new_files_names:
            self.file_name_as_received = file_name
            data_headers = self.get_headers()
            mapped_data = self.read_file(path=self.file_path, file_name=file_name, headers=data_headers)
            process_id = None
            self.get_file_info()
            self.store_history()
            # self.send_data(self.company_id, process_id, mapped_data)
            return mapped_data

