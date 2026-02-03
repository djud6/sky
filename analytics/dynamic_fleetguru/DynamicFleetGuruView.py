from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from core.DynamicFleetGuruManager.DynamicFleetGuruHandler import DynamicFleetGuruHandler
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


# This API will return an array of the least utilized assets for a user's location(s)
# as well as suggestion.
class UnderusedAssets(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DynamicFleetGuruHandler.handle_underused_assets(request.user)