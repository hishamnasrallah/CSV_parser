import csv
import os
import chardet
from app.api.models import MapperProfile, Profile
from app.api.repositories.common import CRUD
from app.api.repositories.csv import get_file_history, get_file_mapper, \
    create_file_history, update_last_run
from app.tasks import send_collected_data
from core.exceptions.csv import ProfileAlreadyDeleted, NoProfileAssigned
from core.exceptions.profile import ProfileIsInactive
from utils.sftp_server import SFTPHelper


class CSVHelper:

    def __init__(self, task_id, company_id, file_id, file_name, file_path,
                 process_id):
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
        self.history_rec = None
        self.sftp_helper = None

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
                history = get_file_history(file_id=self.file_id,
                                           file_name=file)
                if not history.first():
                    final_files.append(file)
        return final_files

    def get_headers(self):
        mappers = get_file_mapper(self.file_id)
        list_header_fields = []
        for mapper in mappers:
            list_header_fields.append(
                {"column_name": mapper.field_name,
                 "mapper_field_name": mapper.map_field_name,
                 "is_ignored": mapper.is_ignored})
        return list_header_fields

    def copy_file_to_tmp_without_sftp(self):
        import shutil
        shutil.copy2(self.file_path + "/" + self.file_name_as_received,
                     self.tmp_path + "/" + self.file_name_as_received)

    def connect_to_sftp(self):
        db = CRUD().db_conn()
        linked_profile = db.query(MapperProfile).filter(
            MapperProfile.mapper_id == self.file_id).first()
        if not linked_profile:
            raise NoProfileAssigned
        profile = db.query(Profile).filter(
            Profile.id == linked_profile.profile_id).first()
        if profile.is_deleted:
            raise ProfileAlreadyDeleted
        if not profile.is_active:
            raise ProfileIsInactive

        with SFTPHelper() as sftp_helper:
            sftp_helper.connect(server_ip=profile.base_server_url,
                                username=profile.server_connection_username,
                                password=profile.server_connection_password)
            sftp_helper.change_dir(path=self.file_path)
            self.sftp_helper = sftp_helper
            new_files_names = self.read_files_by_prefix(prefix=self.file_name)
            if not new_files_names:
                self.task_status = "No files"
                return self.task_status
            for file_name in new_files_names:
                self.file_name_as_received = file_name
                self.copy_file_to_tmp_sftp()
                data_headers = self.get_headers()
                self.get_file_info()
                mapped_data = self.read_file(file_name=file_name,
                                             headers=data_headers)

                self.remove_temp_file(
                    f"{self.current_dir}/tmp/" + self.file_name_as_received)

                x = self.send_data(self.process_id, mapped_data)
                response = {
                    "file_name_as_received": self.file_name_as_received,
                    "core_response": x}
                return response

    def copy_file_to_tmp_sftp(self):
        self.sftp_helper.copy_file_from_server(
            file_name=self.file_name_as_received)

    def remove_temp_file(self, full_file_path):
        os.unlink(full_file_path)

    def read_file(self, file_name=None, headers=None):
        if file_name.endswith('.csv'):
            with open(f"{self.current_dir}/tmp/{file_name}", "rb") as file:
                file_content = file.read()
                detected_encoding = chardet.detect(file_content)['encoding']
                file_content = file_content.decode(detected_encoding)

                mapped_data = []
                reader = csv.reader(file_content.splitlines(), delimiter=',',
                                    skipinitialspace=True)
                header_row = next(reader)  # read the header row
                for each_line in reader:
                    each_record = dict()
                    for column_name in headers:
                        if column_name["is_ignored"] != True:
                            index = header_row.index(
                                column_name["column_name"])
                            if index < len(each_line):
                                value = each_line[index]
                                if value.startswith('="') and value.endswith(
                                        '"'):
                                    value = value[2:-1]
                                each_record[
                                    column_name["mapper_field_name"]] = value
                    mapped_data.append(each_record)
        elif file_name.endswith('.man'):
            with open(f"{self.current_dir}/tmp/{file_name}", "r") as file:
                file_content = file.readlines()
                mapped_data = []
                header_row = file_content[0].strip().split(
                    '\t')  # read the header row
                column_indices = [header_row.index(column["column_name"]) for
                                  column in headers if
                                  not column["is_ignored"]]
                for line in file_content[1:]:
                    each_record = dict()
                    line_values = line.strip().split('\t')
                    for i, index in enumerate(column_indices):
                        column_name = headers[i]["mapper_field_name"]
                        if index < len(line_values):
                            value = line_values[index]
                            if value.startswith('="') and value.endswith('"'):
                                value = value[2:-1]
                            each_record[column_name] = value
                    mapped_data.append(each_record)
        self.history_rec = self.store_history(mapped_data)

        return mapped_data

    def send_data(self, process_id, data):
        responses = []
        for idx, _obj in enumerate(data):
            response = send_collected_data.delay(self.company_id, process_id,
                                                 idx + 1, self.history_rec.id,
                                                 _obj, self.file_id)

            responses.append(response)

        return responses

    def store_history(self, mapped_data):
        total_rows = len(mapped_data)
        history_rec = create_file_history(self.file_id, self.file_size,
                                          self.file_name_as_received,
                                          total_rows=total_rows,
                                          task_id=self.task_id)
        update_last_run(self.file_id)
        return history_rec

    def get_tmp_path(self):
        self.current_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        sub_folder = "tmp"
        self.tmp_path = os.path.join(self.current_dir, sub_folder)

    def get_file_info(self):
        self.timeout += 1
        # // TODO: timeout
        size = os.path.getsize(
            f"{self.current_dir}/tmp/" + self.file_name_as_received)
        self.file_size = size
        try:
            size = os.path.getsize(
                f"{self.current_dir}/tmp/" + self.file_name_as_received)
            self.file_size = size
        except:
            if self.timeout <= 30:
                self.get_file_info()
            else:
                pass

    def main(self):
        self.get_tmp_path()
        result = self.connect_to_sftp()
        return result
