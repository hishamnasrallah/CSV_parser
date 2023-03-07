import csv
import os
import paramiko
from app.api.repositories.csv import get_file_history, get_file_mapper, create_file_history, update_last_run
from app.brokers.decapolis_core import CoreApplicationBroker, send_collected_data
from utils.sftp_server import SFTPHelper


class CSVHelper:

    def __init__(self, task_id, company_id, file_id, file_name, file_path, process_id):
        self.tmp_path = None
        self.file_size = None
        self.file_name_as_received = None
        self.company_id = company_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_id = file_id
        self.task_id = task_id
        self.task_status = None
        self.process_id = process_id
        self.timeout = 0
        self.current_dir = None

    def read_files_by_prefix(self, prefix):
        files = self.sftp_helper.read_files_by_prefix_sftp(prefix)

        new_files = self.is_new_file(files)
        return new_files

    def read_files_by_prefix_without_sftp(self, prefix):
        files = []
        for filename in os.listdir(self.file_path):
            if filename.startswith(prefix):
                with open(os.path.join(self.file_path, filename), 'r') as f:
                    file_name = os.path.basename(f.name)
                    files.append(file_name)
                f.close()
        new_files = self.is_new_file(files)
        return new_files

    def is_new_file(self, files):
        final_files = []
        if files:
            for file in files:
                history = get_file_history(file_id=self.file_id, file_name=file)
                if not history.first():
                    final_files.append(file)

        return final_files

    def get_headers(self):

        mappers = get_file_mapper(self.file_id)
        list_header_fields = []
        for mapper in mappers:
            list_header_fields.append({"column_name": mapper.map_field_name, "is_ignored": mapper.is_ignored})
        return list_header_fields

    def copy_file_to_tmp_without_sftp(self):
        import shutil
        shutil.copy2(self.file_path + "/" + self.file_name_as_received,
                     self.tmp_path + "/" + self.file_name_as_received)

    def connect_to_sftp(self):
        self.sftp_helper = SFTPHelper()
        self.sftp_helper.connect(server_ip=os.environ.get("DELMONTE_SFTP_IP"),
                                 username=os.environ.get("DELMONTE_SFTP_USERNAME"),
                                 password=os.environ.get("DELMONTE_SFTP_PASSWORD"))
        self.sftp_helper.change_dir(path=self.file_path)

    def copy_file_to_tmp_sftp(self):
        self.sftp_helper.copy_file_from_server(path=self.file_path, tmp_path=self.tmp_path,
                                          file_name=self.file_name_as_received)

        self.sftp_helper.close_connection()

    def remove_temp_file(self, full_file_path):
        os.unlink(full_file_path)

    def read_file(self, file_name=None, headers=None):
        with open(f"{self.current_dir}/tmp/{file_name}", "r") as file:

            keys = headers
            headers = []
            for each_key in keys:
                headers.append(each_key)

            mapped_data = []
            reader = csv.reader(file, delimiter=',', skipinitialspace=True)
            for each_line in reader:
                each_record = dict()
                column_index = 0
                for each_column in each_line:
                    if column_index < len(headers):
                        if headers[column_index]["is_ignored"] != True:
                            each_record[headers[column_index]["column_name"]] = each_column
                        column_index += 1
                mapped_data.append(each_record)
        return mapped_data

    def send_data(self, company_id, process_id, data):
        responses = []
        for _obj in data:
            response = send_collected_data(company_id=company_id, process_id=process_id, data=_obj)
            responses.append(response.content)
        return responses


    def store_history(self):
        create_file_history(self.file_id, self.file_size, self.file_name_as_received, task_id=self.task_id)
        update_last_run(self.file_id)

    def get_tmp_path(self):
        self.current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sub_folder = "tmp"
        self.tmp_path = os.path.join(self.current_dir, sub_folder)

    def get_file_info(self):
        self.timeout += 1
        # // TODO: timeout
        size = os.path.getsize(f"{self.current_dir}/tmp/" + self.file_name_as_received)
        self.file_size = size
        try:
            size = os.path.getsize(f"{self.current_dir}/tmp/" + self.file_name_as_received)
            self.file_size = size
        except:
            if self.timeout <= 30:
                self.get_file_info()
            else:
                pass

    def main(self):
        self.get_tmp_path()
        # // TODO: use this function connect_to_sftp nestead of commented it
        self.connect_to_sftp()


        # // TODO: use this function read_files_by_prefix nestead of read_files_by_prefix_without_sftp
        new_files_names = self.read_files_by_prefix(prefix=self.file_name)


        if not new_files_names:
            self.task_status = "No files"
            return self.task_status
        for file_name in new_files_names:
            self.file_name_as_received = file_name
            # // TODO: use this function copy_file_to_tmp_sftp nestead of copy_file_to_tmp_without_sftp
            self.copy_file_to_tmp_sftp()
            # // TODO: use this function copy_file_to_tmp_sftp nestead of copy_file_to_tmp_without_sftp
            data_headers = self.get_headers()
            self.get_file_info()
            mapped_data = self.read_file(file_name=file_name, headers=data_headers)

            self.store_history()
            self.remove_temp_file(f"{self.current_dir}/tmp/" + self.file_name_as_received)

            x = self.send_data(self.company_id, self.process_id, mapped_data)

            return x
