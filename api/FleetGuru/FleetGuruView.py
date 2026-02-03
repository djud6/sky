from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..Models.fleet_guru import FleetGuru
from ..Serializers.serializers import FleetGuruSerializer
from core.FleetGuruManager.FleetGuruHandler import FleetGuruHandler
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class GetInformation(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, _process_name):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return FleetGuruHandler.handle_get_information(_process_name, request.user)
        

