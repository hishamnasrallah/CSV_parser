import csv
import os
from app.api.v1.models import FileReceiveHistory
from app.api.v1.repositories.csv import get_file_history, get_file_mapper


class CSVHelper:

    def __init__(self, company_id, file_id, file_name, file_path):
        self.company_id = company_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_id = file_id

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

                files.pop(file)

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

    def send_data(self):
        pass



    def main(self):
        new_files_names = self.read_files_by_prefix(prefix=self.file_name)
        for file_name in new_files_names:

            data_headers = self.get_headers()
            mapped_data = self.read_file(path=self.file_path, file_name=file_name, headers=data_headers)

            self.send_data()
            return mapped_data

