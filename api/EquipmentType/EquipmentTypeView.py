from core.EquipmentTypeManager.EquipmentTypeHandler import EquipmentTypeHandler
from core.AssetTypeManager.AssetTypeHandler import AssetTypeHandler
from core.AssetTypeChecksManager.AssetTypeChecksHandler import AssetTypeChecksHandler
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

    # ---------------------------------------------------------------------------------------------------------------------

class AddEquipmentType(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return EquipmentTypeHandler.handle_add_equipment_type(request.data, request.user)

    # ---------------------------------------------------------------------------------------------------------------------

class GetAllEquipmentTypes(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return EquipmentTypeHandler.handle_get_all_equipment_types(request.user)

    # ---------------------------------------------------------------------------------------------------------------------

class UpdateEquipmentType(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return EquipmentTypeHandler.handle_update_equipment_type(request.data, request.user)

    # ---------------------------------------------------------------------------------------------------------------------

class GetAssetTypesWithChecks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetTypeHandler.handle_get_asset_types_with_checks(request.user)

    # ---------------------------------------------------------------------------------------------------------------------

class GetAssetTypesWithoutChecks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetTypeHandler.handle_get_asset_types_without_checks(request.user)

    # ---------------------------------------------------------------------------------------------------------------------

class AddAssetTypeChecks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetTypeChecksHandler.handle_add_asset_type_checks(request.data, request.user)

    # ---------------------------------------------------------------------------------------------------------------------

class UpdateAssetTypeChecks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetTypeChecksHandler.handle_update_asset_type_checks(request.data, request.user)

    # ---------------------------------------------------------------------------------------------------------------------

class GetAssetTypeChecks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetTypeHandler.handle_get_asset_type_checks(request.user)

    # ---------------------------------------------------------------------------------------------------------------------


