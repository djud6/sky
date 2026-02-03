from ..FileManager.FileHelper import FileHelper
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)



class FileSecurity():

    malicious_strings = [
        ""
    ]

    @staticmethod
    def check_files_for_injection(files):
        for _file in files:
            if(FileSecurity.check_file_for_injection(_file)):
                return True
        return False


    @staticmethod
    def check_file_for_injection(_file):
        string = FileHelper.file_to_base64(_file.read())
