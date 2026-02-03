class FileInfo:

    def __init__(self, file_name="NA", file_type="NA", bytes=0, file_path="NA", file_url="NA", blob_container="NA", blob=None, file=None):
        self.file_name = file_name
        self.file_type = file_type
        self.bytes = bytes
        self.file_path = file_path # file_path needs to include the name of the file
        self.file_url = file_url
        self.blob_container = blob_container
        self.blob_name = self.set_blob_name()
        self.blob = blob # Holds a blob storage blob
        self.file = file # Holds the actual file data object

    def set_blob_name(self):
        blob_name = self.file_url.split("blob.core.windows.net/" + self.blob_container + '/')
        if len(blob_name) > 0:
            return blob_name[-1]
        else:
            return "NA"