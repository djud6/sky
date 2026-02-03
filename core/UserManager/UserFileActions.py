
from api_auth.Auth_User import User
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class UserFileActions():
    
    @staticmethod
    def create_user_image_record(detailed_user_obj, url):
        detailed_user_obj.image_url = url
        detailed_user_obj.save()
        return detailed_user_obj