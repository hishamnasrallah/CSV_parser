import os
import csv
import time


class UploadHelper:

    def __init__(self, upload_file):
        self.new_filename = None
        self.upload_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.timestamp = int(time.time())
        self.uploaded_file = upload_file

    def make_directory_if_not_exists(self):
        is_exist = os.path.exists(os.path.join(self.upload_dir, "media_uploads"))
        if not is_exist:
            os.makedirs(os.path.join(self.upload_dir, "media_uploads"))

    def handle_file_name(self):
        _, file_extension = os.path.splitext(self.uploaded_file.filename)
        self.new_filename = f"{_}_{self.timestamp}{file_extension}"
        return self.new_filename

    def save_file(self):
        try:
            self.make_directory_if_not_exists()
            self.handle_file_name()
            file_path = os.path.join(self.upload_dir, "media_uploads", self.new_filename)
            contents = self.uploaded_file.file.read()
            # Save the file to the specified directory
            with open(file_path, 'wb') as f:
                f.write(contents)

        except Exception:
            return {"message": "There was an error uploading the file"}

        finally:
            self.uploaded_file.file.close()
            file_name = self.uploaded_file.filename
            content_type = self.uploaded_file.content_type
            size =  size = os.path.getsize(file_path)
            return {"data": {"file_path": file_path, "file_name": file_name, "content_type": content_type, "size": size}
                , "message": f"Successfully uploaded {self.uploaded_file.filename}"}

    def read_csv(self, file_path: str):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            return list(reader)