from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api_vendor.Auth.AuthHelper import AuthHelper
from core.AssetRequestManager.AssetRequestHandler import AssetRequestHandler
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.Helper import HelperMethods
from types import SimpleNamespace

from GSE_Backend.errors.ErrorDictionary import CustomError
import logging


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


# OUTBOUND -----------------------------------------------------------------------------------

"""
    APIs that send out requests to the vendor system go here.
"""

# INBOUND ------------------------------------------------------------------------------------

"""
    APIs that process requests internally go here.
"""


class GetAssetRequests(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return AssetRequestHandler.handle_get_asset_requests_for_vendor(request.data)


class GetAssetRequestDetails(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return AssetRequestHandler.handle_get_asset_request_details_for_vendor(request.data)


class UpdateAssetRequestStatus(APIView):
    permission_classes = [AllowAny]

    def post(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = HelperMethods.json_str_to_dict(request.POST["data"])

            client_name = data.get("client_name")
            auth_company, resp = VendorOpsHelper.get_auth_db_company_by_name(client_name)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
                
            db_name = auth_company.company_db_access

            asset_request_id = data.get("asset_request_id")
            file_specs = HelperMethods.json_str_to_dict(request.POST["file_specs"])
            request_files = request.FILES.getlist("files")
            user = SimpleNamespace(
                            db_access=db_name,
                            email=None
                        )

            # Update status
            status_update_response = AssetRequestHandler.handle_update_asset_request_status(
                data,
                user.email,
                db_name,
                update_vendor=False
            )

            if status_update_response.status_code != status.HTTP_202_ACCEPTED:
                return status_update_response

            # Upload files
            if len(request_files) > 0 :
                file_upload_response = AssetRequestHandler.handle_add_supporting_files(
                    asset_request_id,
                    file_specs,
                    request_files,
                    user    
                )
                if file_upload_response.status_code != status.HTTP_200_OK:
                    return file_upload_response

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class UploadAssetRequestFiles(APIView):
    permission_classes = [AllowAny]

    def post(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = HelperMethods.json_str_to_dict(request.POST["data"])

            client_name = data.get("client_name")
            auth_company, resp = VendorOpsHelper.get_auth_db_company_by_name(client_name)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
                
            db_name = auth_company.company_db_access
            
            asset_request_id = data.get("asset_request_id")
            file_specs = HelperMethods.json_str_to_dict(request.POST["file_specs"])
            request_files = request.FILES.getlist("files")
            user = SimpleNamespace(db_access=db_name, email=None)

            return AssetRequestHandler.handle_add_supporting_files(
                asset_request_id, file_specs, request_files, user
            )

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )