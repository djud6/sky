from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from rest_framework.permissions import AllowAny
from api_vendor.Auth.AuthHelper import AuthHelper
from core.MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from core.RequestQuoteManager.RequestQuoteHandler import RequestQuoteHandler
from core.RequestQuoteManager.RequestQuoteHelper import RequestQuoteHelper
from core.RequestQuoteManager.RequestQuoteUpdater import RequestQuoteUpdater
from core.AssetRequestManager.AssetRequestHandler import AssetRequestHandler
from core.AssetRequestManager.AssetRequestHelper import AssetRequestHelper
from core.MaintenanceManager.MaintenanceHandler import MaintenanceHandler
from core.RepairManager.RepairHandler import RepairHandler
from core.RepairManager.RepairHelper import RepairHelper
from core.DisposalManager.DisposalHandler import DisposalHandler
from core.DisposalManager.DisposalHelper import DisposalHelper
from core.TransferManager.TransferHandler import TransferHandler
from core.TransferManager.TransferHelper import TransferHelper
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.Helper import HelperMethods
from types import SimpleNamespace
from datetime import datetime

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

class ApproveQuote(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, request_quote_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return RequestQuoteHandler.handle_approve_quote(request_quote_id, request.user)

class RejectAssetQuote(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, asset_request_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return RequestQuoteHandler.handle_reject_asset_quote(asset_request_id, request.user)

class RejectMaintenanceQuote(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, maintenance_request_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return RequestQuoteHandler.handle_reject_maintenance_quote(maintenance_request_id, request.user)

class RejectDisposalQuote(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, disposal_request_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return RequestQuoteHandler.handle_reject_disposal_quote(disposal_request_id, request.user)

class RejectRepairQuote(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, repair_request_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return RequestQuoteHandler.handle_reject_repair_quote(repair_request_id, request.user)

class RejectTransferQuote(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, transfer_request_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return RequestQuoteHandler.handle_reject_transfer_quote(transfer_request_id, request.user)

# Rejects list of specific quotes
class RejectQuotes(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return RequestQuoteHandler.handle_reject_quotes(request.user, request.data)

# INBOUND ------------------------------------------------------------------------------------

"""
    APIs that process requests internally go here.
"""

class UpdateQuote(APIView):
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

            vendor_name = data.get("vendor_name")
            file_specs = HelperMethods.json_str_to_dict(request.POST["file_specs"])
            request_files = request.FILES.getlist("files")

            estimated_cost = data.get("estimated_cost")
            request_custom_id = data.get("request_custom_id")
            request_type = request_custom_id.split("-")[1]
            request_id = request_custom_id.split("-")[2]
            user = SimpleNamespace(db_access=db_name, email=None)

            # Upload quote
            if len(request_files) > 0 :
                current_date = datetime.utcnow()

                if request_type == "ar":
                    asset_request, resp = AssetRequestHelper.get_asset_request_by_id(request_id, user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp
                    if (
                        (asset_request.quote_deadline is None)
                        or
                        (current_date.timestamp() <= asset_request.quote_deadline.timestamp())
                    ):

                        # Upload quote file
                        upload_resp = AssetRequestHandler.handle_add_supporting_files(
                            request_id,
                            file_specs,
                            request_files,
                            user    
                        )
                        if upload_resp.status_code != status.HTTP_200_OK:
                            return upload_resp                       
                    else:
                        return Response(
                            CustomError.get_full_error_json(CustomError.RQUF_0),
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                elif request_type == "d":
                    disposal_obj, resp = DisposalHelper.get_disposal_request_by_id(request_id, user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp

                    if (
                        (disposal_obj.quote_deadline is None)
                        or
                        (current_date.timestamp() <= disposal_obj.quote_deadline.timestamp())
                    ):

                        # Upload quote file
                        upload_resp = DisposalHandler.handle_add_supporting_files(
                            disposal_obj,
                            file_specs,
                            request_files,user.email, 
                            user.db_access
                        )
                        if upload_resp.status_code != status.HTTP_200_OK:
                            return upload_resp
                    else:
                        return Response(
                            CustomError.get_full_error_json(CustomError.RQUF_0),
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                elif request_type == "m":
                    maint_obj, resp = MaintenanceHelper.get_maintenance_request_by_id(request_id, user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp

                    if (
                        (maint_obj.quote_deadline is None)
                        or
                        (current_date.timestamp() <= maint_obj.quote_deadline.timestamp())
                    ):

                        # Upload quote file
                        upload_resp = MaintenanceHandler.handle_add_supporting_files(
                            request_id,
                            file_specs,
                            request_files,
                            user    
                        )
                        if upload_resp.status_code != status.HTTP_200_OK:
                            return upload_resp
                    else:
                        return Response(
                            CustomError.get_full_error_json(CustomError.RQUF_0),
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                elif request_type == "r":
                    repair_obj, resp = RepairHelper.get_repair_request_by_id(request_id, user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp

                    if (
                        (repair_obj.quote_deadline is None)
                        or
                        (current_date.timestamp() <= repair_obj.quote_deadline.timestamp())
                    ):

                        # Upload quote file
                        upload_resp = RepairHandler.handle_add_supporting_files(
                            repair_obj,
                            file_specs,
                            request_files,
                            user
                        )
                        if upload_resp.status_code != status.HTTP_200_OK:
                            return upload_resp
                    else:
                        return Response(
                            CustomError.get_full_error_json(CustomError.RQUF_0),
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                elif request_type == "t":
                    transfer_obj, resp = TransferHelper.get_transfer_by_id(request_id, user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp

                    if (
                        (transfer_obj.quote_deadline is None)
                        or
                        (current_date.timestamp() <= transfer_obj.quote_deadline.timestamp())
                    ):
                        # Upload quote file
                        upload_resp = TransferHandler.handle_add_supporting_files(
                            transfer_obj,
                            file_specs,
                            request_files,
                            user
                        )
                        if upload_resp.status_code != status.HTTP_200_OK:
                            return upload_resp
                    else:
                        return Response(
                            CustomError.get_full_error_json(CustomError.RQUF_0),
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    
                # Get quote
                quote = RequestQuoteHelper.get_quote_by_request_custom_id_and_vendor_name(
                    request_custom_id,
                    vendor_name,
                    db_name
                )

                # Update quote entry
                updated_quote, update_resp = RequestQuoteUpdater.update_quote_fields(
                    quote,
                    {"estimated_cost": estimated_cost}
                )
                if update_resp.status_code != status.HTTP_202_ACCEPTED:
                    return update_resp

            return RequestQuoteHandler.handle_update_quote(data, user)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )