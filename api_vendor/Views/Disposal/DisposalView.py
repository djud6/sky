from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from types import SimpleNamespace
from rest_framework.permissions import AllowAny
from api_vendor.Auth.AuthHelper import AuthHelper
from api.Models.asset_disposal import AssetDisposalModel
from core.DisposalManager.DisposalHandler import DisposalHandler
from core.DisposalManager.DisposalHelper import DisposalHelper
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.Helper import HelperMethods

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


class GetDisposalRequests(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return DisposalHandler.handle_get_disposals_for_vendor(request.data)
        

class GetDisposalRequestDetails(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return DisposalHandler.handle_get_disposal_details_for_vendor(request.data)


class UpdateDisposalStatus(APIView):
    permission_classes = [AllowAny]

    def post(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            instructions = HelperMethods.json_str_to_dict(request.POST["data"])
            
            client_name = instructions.get("client_name")
            auth_company, resp = VendorOpsHelper.get_auth_db_company_by_name(client_name)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
                
            db_name = auth_company.company_db_access

            disposal_type = instructions.get("disposal_type")
            file_specs = HelperMethods.json_str_to_dict(request.POST["file_specs"])
            files = request.FILES.getlist("files")
            user = SimpleNamespace(
                            db_access=db_name,
                            email=None
                        )

            if disposal_type == AssetDisposalModel.auction:
                return DisposalHandler.handle_update_auction_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            elif disposal_type == AssetDisposalModel.company_directed_sale:
                return DisposalHandler.handle_update_company_directed_sale_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            elif disposal_type == AssetDisposalModel.donate:
                return DisposalHandler.handle_update_donation_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            elif disposal_type == AssetDisposalModel.repurpose:
                return DisposalHandler.handle_update_repurpose_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            elif disposal_type == AssetDisposalModel.scrap:
                return DisposalHandler.handle_update_scrap_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            elif disposal_type == AssetDisposalModel.trade_in:
                return DisposalHandler.handle_update_trade_in_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            elif disposal_type == AssetDisposalModel.transfer:
                return DisposalHandler.handle_update_transfer_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            elif disposal_type == AssetDisposalModel.write_off:
                return DisposalHandler.handle_update_write_off_disposal_status(
                    instructions,
                    file_specs,
                    files,
                    user
                )
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADUF_0))
                return Response(
                CustomError.get_full_error_json(CustomError.ADUF_0),
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )


class UploadDisposalFiles(APIView):
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

            disposal_id = data.get("disposal_id")
            file_specs = HelperMethods.json_str_to_dict(request.POST["file_specs"])
            request_files = request.FILES.getlist("files")
            user = SimpleNamespace(db_access=db_name, email=None)

            disposal_obj, res = DisposalHelper.get_disposal_request_by_id(disposal_id, db_name)
            if res.status_code != status.HTTP_302_FOUND:
                return res

            return DisposalHandler.handle_add_supporting_files(
                disposal_obj, file_specs, request_files, user.email, user.db_access
            )

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )
