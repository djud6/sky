from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..Serializers.serializers import LinkedUserModelSerializer, DetailedUserSerializer
from core.UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework import status
from .db_constants import Constants
import logging
from .AuthViewHelper import token_expire_refresh_handler, expires_in
from datetime import timedelta
from django.conf import settings


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

# to refresh the user token
class RefreshAuthToken(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            token = request.data["token"]
            if Token.objects.using(Constants.AUTH_DB).filter(key=token).exists():
                token = Token.objects.using(Constants.AUTH_DB).get(key=token)
                token = token_expire_refresh_handler(token)            
                token_expiration = token.created + timedelta(seconds = settings.TOKEN_EXPIRED_AFTER_SECONDS)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
                return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
            try:
                return Response({
                    'token': token.key,
                    'token_expiration' : token_expiration,
                }, status=status.HTTP_200_OK)

            except Exception as e:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        except:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)