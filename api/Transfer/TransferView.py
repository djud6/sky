from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.Models.asset_transfer import AssetTransfer
from core.Helper import HelperMethods
from core.TransferManager.TransferHandler import TransferHandler
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AddTransfer(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_add_transfer(request, request.user)


class UpdateTransferStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_update_transfer_status(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                           HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                           request.FILES.getlist('files'), request.user)


class GetTransfersForUserLocation(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_get_transfers_for_user_location(request)

class GetTransfersForUserLocationByVIN(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, _vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_get_transfers_for_user_location_by_vin(request, _vin)


class GetAssetTransfersList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_get_asset_transfer_list(request.user)


class GetTransferDetailByID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, transfer_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_get_asset_transfer_by_id(transfer_id, request.user)


class GetTransferDetailByCustomID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, custom_transfer_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_get_asset_transfer_by_custom_id(custom_transfer_id, request.user)


class UpdateTransfer(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return TransferHandler.handle_update_transfer(request.data, request.user)


# Add files to an asset transfer request
class AddTransferFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request, transfer_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        file_specs = HelperMethods.json_str_to_dict(request.POST['file_specs'])
        transfer_obj = AssetTransfer.objects.get(asset_transfer_id=transfer_id)
        return TransferHandler.handle_add_supporting_files(transfer_obj, file_specs, request.FILES.getlist('files'), request.user)
