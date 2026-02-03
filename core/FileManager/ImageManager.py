import base64
import imghdr
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ImageManager():

    @staticmethod
    def images_from_base64(base64_images):

        try:
            image_data_list = list()
            for image_str in base64_images:
                image_data = base64.b64decode(image_str)
                image_data_list.append(image_data)

            return image_data_list

        except Exception as e:
            Logger.getLogger().error(e)
            return None

    # -----------------------------------------------------------------------
    
    valid_image_types = ["jpeg", "png"]

    @staticmethod
    def verify_files_are_images(files):
        for _file in files:
            if(not ImageManager.verify_file_is_image(_file)):
                return False
        return True    

    @staticmethod
    def verify_file_is_image(_file):
        file_type = str(imghdr.what(_file))
        if(file_type.strip() in ImageManager.valid_image_types):
            return True
        else:
            return False