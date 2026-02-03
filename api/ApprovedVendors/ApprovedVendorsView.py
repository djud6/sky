from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..Models.approved_vendors import ApprovedVendorsModel
from ..Serializers.serializers import (
    ApprovedVendorSerializer,
    LightApprovedVendorSerializer
    )
from core.ApprovedVendorsManager.ApprovedVendorsHandler import ApprovedVendorsHandler
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class GetApprovedVendorByTaskAndDepartment(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, _dep_id, _task_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return ApprovedVendorsHandler.handle_get_approved_vendors_by_task_and_department(_dep_id, _task_id, request.user)

class GetDepartments(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return ApprovedVendorsHandler.handle_get_departments(request.user)

class GetTasks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return ApprovedVendorsHandler.handle_get_tasks(request.user)

class GetVendorsByDepartment(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, _dep_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return ApprovedVendorsHandler.handle_get_vendors_by_department(_dep_id, request.user)

class GetVendorsByTask(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, _task_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return ApprovedVendorsHandler.handle_get_vendors_by_task(_task_id, request.user)

class GetAllVendors(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return ApprovedVendorsHandler.handle_get_all_vendors(request.user)