""" Docstring for the file_manager.py file.

"""
import logging
import os
import time
import zipfile


class FileManager:
    """
    This module defines the FileManager class, which manages files in the download folder. It provides methods to wait
    for the arrival of a file, unzip it, rename the contents, and clean up the original zip file.
    """
    def __init__(self, download_path: str, file_prefix: str, file_suffix: str):
        """
        Constructor for the FileManager class. It initializes the object with the directory and file naming criteria for
        managing downloaded files.

        :param download_path: The directory path where files are downloaded.
        :param file_prefix: The prefix of the file to wait for and unzip.
        :param file_suffix: The suffix of the file to unzip and rename.
        """
        self.download_path = download_path
        self.file_prefix = file_prefix
        self.file_suffix = file_suffix
        self.logger = logging.getLogger(__name__)

    def wait_for_download(self, timeout: int = 6000, check_interval: int = 10) -> [str, None]:
        """
        Waits for a file with the specified prefix to appear in the download folder. It checks for the file at regular
        intervals and returns the path of the file once it appears.

        :param timeout: The maximum time to wait for the file in seconds. Default is 6000 seconds.
        :param check_interval: The interval in seconds to wait between checks. Default is 10 seconds.
        :return: The full path of the downloaded file if found, otherwise None.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check for files that start with the specified prefix
            for filename in os.listdir(self.download_path):
                if filename.startswith(self.file_prefix) and filename.endswith('.zip'):
                    return os.path.join(self.download_path, filename)
            time.sleep(check_interval)
        return None

    def unzip_and_rename(self, zip_file_path: str, new_name: str):
        """
        Unzips the specified zip file and renames the extracted file according to the given new name. It also removes
        the original zip file after extraction.

        :param zip_file_path: The path of the zip file to unzip.
        :param new_name: The new name to assign to the extracted file.
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
        # pylint: disable=broad-except
        except Exception as e:
            print(f"Error unzipping or renaming the file - {zip_file_path}: {e}")
