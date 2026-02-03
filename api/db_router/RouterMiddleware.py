from re import sub
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token
from threading import local
from api_auth.Auth_DB.DBMethods import DBMethods
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
my_local_global = local()

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class RouterMiddleware(MiddlewareMixin):

    def process_request(self, request):
    
        header_token = request.META.get('HTTP_AUTHORIZATION', None)

        if header_token is not None and 'Token' in header_token:
            token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
            token_obj = Token.objects.filter(key = token)
            if token_obj:
                token_obj = Token.objects.get(key = token)
                request.user = token_obj.user
                my_local_global.cfg = None
                dbname = DBMethods.GetDBName(request.user.id)
                my_local_global.cfg = dbname

    def process_response(self, request, response):
        if hasattr( my_local_global, 'cfg' ):
            my_local_global.__dict__.clear()
        return response

    def process_exception(self, request, exception):
        if hasattr( my_local_global, 'cfg' ):
            my_local_global.__dict__.clear()
        return None