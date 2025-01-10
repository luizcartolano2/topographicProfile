import os
import time
import zipfile


class FileManager:
    def __init__(self, download_path, file_prefix, file_suffix):
        self.download_path = download_path
        self.file_prefix = file_prefix
        self.file_suffix = file_suffix

    def wait_for_download(self, timeout=6000, check_interval=10):
        """
        Wait until a file with the specified prefix appears in the download folder.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check for files that start with the specified prefix
            for filename in os.listdir(self.download_path):
                if filename.startswith(self.file_prefix) and filename.endswith('.zip'):
                    return os.path.join(self.download_path, filename)
            time.sleep(check_interval)
        return None

    def unzip_and_rename(self, zip_file_path, new_name):
        """
        Unzip the file and rename it.
        """
        try:
            # Unzip the file
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.download_path)

            # Assuming the zip file contains only one file, get its name
            extracted_files = os.listdir(self.download_path)
            for file in extracted_files:
                # Rename the extracted file
                if file.startswith(self.file_prefix) and file.endswith(self.file_suffix):
                    extracted_file_path = os.path.join(self.download_path, file)
                    os.rename(extracted_file_path, os.path.join(self.download_path, new_name))
                    print(f"Renamed {file} to {new_name}")
                    break

            # Remove the original zip file
            os.remove(zip_file_path)
            print(f"Removed the original file: {zip_file_path}")

        except Exception as e:
            print(f"Error unzipping or renaming the file - {zip_file_path}: {e}")
