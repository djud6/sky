import logging

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from GSE_Backend.errors.ErrorDictionary import CustomError
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from core.EngineManager.EngineHandler import EngineHandler

class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class Add(APIView):
    def post(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return EngineHandler.handle_add(request.user,request.data)


class Remove(APIView):
    def post(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return EngineHandler.handle_remove(request.user,request.data)


class Update(APIView):
    def post(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return EngineHandler.handle_update(request.user,request.data)


class GetHistory(APIView):
    def get(self,request,id):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return EngineHandler.handle_get_history(request.user,id)


class GetByID(APIView):
    def get(self,request,id):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return EngineHandler.handle_get(request.user,id)


class GetByVIN(APIView):
    def get(self,request,vin):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return EngineHandler.handle_get_by_vin(request.user,vin)


class GetHistoryByVIN(APIView):
    def get(self,request,vin):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return EngineHandler.handle_get_history_by_vin(request.user,vin)


class IsUsageValid(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return EngineHandler.handle_is_usage_valid(request.data, request.user)
