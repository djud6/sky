from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..Serializers.serializers import ErrorReport
from ..Models.error_report import ErrorReport
from core.Helper import HelperMethods
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from core.ErrorReportManager.ErrorReportHandler import ErrorReportHandler
from GSE_Backend.errors.ErrorDictionary import CustomError

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class CreateErrorReport(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        data = HelperMethods.json_str_to_dict(request.POST['data'])
        images = request.FILES.getlist('files')
        return ErrorReportHandler.handle_create_error_report(data, images, request.user)