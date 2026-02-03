from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import json
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
import os

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ParsingHelper():

    @staticmethod
    def parse_database_details_env_var(db_details_env_var):
        '''
        Expects that the input string will have each database dictionary split by &%&
        '''
        try:
            full_db_details_dict = {}
            for item in db_details_env_var.replace(' ', '').replace("'", '"').replace('\\', '').split('&%&'):
                if not item.strip():
                    continue  # skip empty segments
                item = json.loads(item)
                cur_db_details = {
                    'ENGINE': settings.DATABASE_CONSTANTS.get('ENGINE'),
                    'NAME': item.get('db_name'),
                    'USER': settings.DATABASE_CONSTANTS.get('USER'),
                    'PASSWORD': settings.DATABASE_CONSTANTS.get('PASSWORD'),
                    'HOST': settings.DATABASE_CONSTANTS.get('HOST'),
                    'PORT': settings.DATABASE_CONSTANTS.get('PORT'),
                    'CONN_MAX_AGE': settings.DATABASE_CONSTANTS.get('CONN_MAX_AGE'),
                    'OPTIONS': settings.DATABASE_CONSTANTS.get('OPTIONS')
                }
                full_db_details_dict[item.get('db_access')] = cur_db_details
            return full_db_details_dict
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return {}

    @staticmethod
    def parse_blob_connection_strings_env_var(blob_con_str_env_var):
        try:
            return json.loads(blob_con_str_env_var.replace("'", '"').replace('\\', ''))
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return {}
