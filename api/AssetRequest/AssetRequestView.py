from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.AssetRequestManager.AssetRequestHandler import AssetRequestHandler
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


# Returns all asset types
class GetAssetTypes(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_get_asset_types(request.user)

# Update asset type
class UpdateAssetType(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        asset_type_id = request.data.get('id')
        if not asset_type_id:
            Logger.getLogger().error(CustomError.get_full_error_json(CustomError.G_0, 'Asset Type ID is missing'))
            return Response(CustomError.get_full_error_json(CustomError.G_0, 'Asset Type ID is missing'), status=status.HTTP_400_BAD_REQUEST)
        response = AssetRequestHandler.handle_update_asset_type(asset_type_id, request.data, request.user)
        return response

# Add Custom Field to Asset Type
class AddAssetTypeCustomField(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, asset_type_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if not asset_type_id:
            Logger.getLogger().error(CustomError.get_full_error_json(CustomError.G_0, 'Asset Type ID is missing'))
            return Response(CustomError.get_full_error_json(CustomError.G_0, 'Asset Type ID is missing'), status=status.HTTP_400_BAD_REQUEST)
        response = AssetRequestHandler.handle_update_asset_type_custom_field(asset_type_id, request.data, request.user)
        return response
        
class DeleteAssetTypeCustomField(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, asset_type_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if not asset_type_id:
            Logger.getLogger().error(CustomError.get_full_error_json(CustomError.G_0, 'Asset Type ID is missing'))
            return Response(CustomError.get_full_error_json(CustomError.G_0, 'Asset Type ID is missing'), status=status.HTTP_400_BAD_REQUEST)
        response = AssetRequestHandler.handle_delete_asset_type_custom_field(asset_type_id, request.data, request.user)
        return response

# returns all manufacturers avilable for a given asset type
class GetManufacturerByAssetType(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, asset_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_get_manufacturer_by_asset_type(asset_id, request.user)


# This class returns equipment type based on a given asset type and asset manufacturer
class GetEquipment(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, asset_id, manufacturer_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_get_equipment(asset_id, manufacturer_id, request.user)


class GetJustifications(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_get_justifications(request.user)        


class AddAssetRequest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_add_asset_request(request.data, request.user)


class ListInProgressAssetRequests(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_list_in_progress_asset_requests(request.user)


class ListDeliveredAssetRequests(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_list_delivered_asset_requests(request.user)


class GetAssetRequestDetailsByID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, asset_request_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_get_asset_request_details_by_id(asset_request_id, request.user)


class GetAssetRequestDetailsByCustomID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, asset_request_custom_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_get_asset_request_details_by_custom_id(asset_request_custom_id, request.user)


class UpdateAssetRequestStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_update_asset_request_status(request.data, request.user)
    

class UpdateAssetRequest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetRequestHandler.handle_update_asset_request(request.data, request.user)
