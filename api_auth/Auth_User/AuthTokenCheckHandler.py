from .AuthViewHelper import token_expire_check
from rest_framework.authtoken.models import Token
from api_auth.Auth_User.db_constants import Constants
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

def auth_token_check(user):

    token = Token.objects.using(Constants.AUTH_DB).get(user=user)
    if token:
        is_expired = token_expire_check(token)
    return is_expired
    