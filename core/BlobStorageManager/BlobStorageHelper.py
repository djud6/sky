from core.Helper import HelperMethods
from multiprocessing.pool import ThreadPool
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from django.conf import settings
import uuid
from ..FileManager.FileInfo import FileInfo
from datetime import datetime, timedelta
import logging
from datetime import datetime, timedelta
import re

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)
   
    
class BlobStorageHelper():

    @staticmethod
    def write_files_to_blob(files, container_name, prefix, company_name, db_name):
        file_infos = []
        for _file in files:
            status, file_info = BlobStorageHelper.write_file_to_blob(_file, container_name, prefix, company_name, db_name)
            print("status: " + str(status))
            print("name: " + file_info.file_name)
            print("url: " + file_info.file_url)
            print("type: " + file_info.file_type)
            print("bytes: " + str(file_info.bytes))
            if(not status):
                return False, None
            file_infos.append(file_info)
        return True, file_infos

    # -----------------------------------------------------------------------

    @staticmethod
    def write_file_to_blob(_file, container_name, prefix, company_name, db_name):
        try:
            connection_string = settings.CONNECTION_STRINGS.get(str(db_name).strip())
            blob = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=BlobStorageHelper.create_generic_blob_name(prefix, company_name))
            blob.upload_blob(_file, content_settings=ContentSettings(content_type=_file.content_type))
            #blob.close
            return True, FileInfo(file_name=_file.name, file_url=str(blob.url), file_type=str(_file.content_type), bytes=_file.size)
        except Exception as e:
            Logger.getLogger().error(e)
            return False, None

    # -----------------------------------------------------------------------

    @staticmethod
    def delete_file_from_blob(blob_name, container_name, db_name):
        try:
            connection_string = settings.CONNECTION_STRINGS.get(str(db_name).strip())
            blob = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=blob_name)
            blob.delete_blob()
            #blob.close
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False
 
    # -----------------------------------------------------------------------

    @staticmethod
    def create_generic_blob_name(prefix, company_name):
        dateTimestmp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        file_name = company_name + "_" + prefix + dateTimestmp
        return str(uuid.uuid4()) + "_" + file_name.replace(" ", "_")

# -----------------------------------------------------------------------

    @staticmethod
    def get_exact_account_info(connection_string):
        connection_val = connection_string.split(';')
        mydict = {}
        for i in connection_val:
            j = i.split('=')
            mydict[j[0]]=j[1]
        return mydict

# -----------------------------------------------------------------------

    @staticmethod
    def get_blob_sas(account_name, account_key, container_name, blob_name):
        sas = generate_blob_sas( account_name=account_name,
                                    container_name=container_name,
                                    blob_name=blob_name,
                                    account_key=account_key,
                                    permission=BlobSasPermissions(read=True),
                                    expiry=datetime.utcnow() + timedelta(hours=1))
        return sas

# -----------------------------------------------------------------------

    @staticmethod
    def get_secure_blob_url(db_name, blob_container, file_url):
        invalid_urls = [None, "NA", "N/A", ""]
        if file_url not in invalid_urls:
            connection_string = settings.CONNECTION_STRINGS.get(str(db_name).strip())
            account_info = BlobStorageHelper.get_exact_account_info(connection_string)
            account_name = account_info['AccountName']
            account_key = account_info['AccountKey'] + '=='
            blob_name = file_url.rsplit('/', 1)[-1]
            blob = BlobStorageHelper.get_blob_sas(str(account_name), str(account_key), blob_container, str(blob_name))
            blob_url = 'https://'+str(account_name)+'.blob.core.windows.net/'+str(blob_container)+'/'+str(blob_name)+'?'+str(blob)
            return blob_url
        else:
            return file_url

# -----------------------------------------------------------------------

    @staticmethod
    def get_file_from_blob(db_name, blob_container, file_url):
        connection_string = settings.CONNECTION_STRINGS.get(str(db_name).strip())
        blob_name = HelperMethods.name_from_end_of_url(file_url, '/')
        blob = BlobClient.from_connection_string(conn_str=connection_string, container_name=blob_container, blob_name=blob_name)
        data = blob.download_blob().readall()
        return data

# -----------------------------------------------------------------------

    @staticmethod
    def get_files_from_blob(db_name, blob_container_name, file_infos):
        '''
        Requires the company name to match against the right blob storage connection string in settings.py
        Also requires a list of FileInfo objects with the following fields filled out: file_url and blob_name.

        This method outputs the sub-list of FileInfo objects it received which it could match with the
        blobs inside the specified container and fills the blob and file fields of said FileInfo objects.
        '''
        def download_blob(file_info):
            file = blob_container.get_blob_client(file_info.blob).download_blob().readall()
            file_info.file = file
            return file_info

        connection_string = settings.CONNECTION_STRINGS.get(str(db_name).strip())
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_container = blob_service_client.get_container_client(blob_container_name)

        blobs = blob_container.list_blobs()

        relevant_file_infos = []
        for blob in blobs:
            for file_info in file_infos:
                if file_info.blob_name == blob.name:
                    file_info.blob = blob
                    relevant_file_infos.append(file_info)

        with ThreadPool(processes=int(10)) as pool:
            return pool.map(download_blob, relevant_file_infos)

# -----------------------------------------------------------------------

    @staticmethod
    def clean_container_name(name):
        name = re.sub('[^a-zA-Z0-9 \n\.\_]', '-', name).replace(' ', '-')
        pattern = "(?P<char>[" + re.escape('-') + "])(?P=char)+"
        name = re.sub(pattern, r"\1", name)
        return name