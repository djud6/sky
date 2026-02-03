from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.DisposalManager.DisposalHandler import DisposalHandler
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
from core.Helper import HelperMethods

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class AddCompanyDirectedSaleDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        
        data = HelperMethods.json_str_to_dict(request.POST['data'])

        # Check if primary_vendor_email is missing or empty, and set a default value
        if not data.get('primary_vendor_email'):
            data['primary_vendor_email'] = 'default_primary_vendor_email@example.com'

        # Check if vendor_email is missing or empty, and set a default value
        if not data.get('vendor_email'):
            data['vendor_email'] = 'default_vendor_email@example.com'
        
        return DisposalHandler.handle_add_company_directed_sale(HelperMethods.json_str_to_dict(request.POST['data']),
                                                                HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                request.FILES.getlist('files'), request.user)
class AddAuctionDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_add_auction_disposal(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                           HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                           request.FILES.getlist('files'), request.user)

class AddRepurposeDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_add_repurpose_disposal(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                            HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                            request.FILES.getlist('files'), request.user)

class AddScrapDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_add_scrap_disposal(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                        HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                        request.FILES.getlist('files'), request.user)

class AddDonationDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_add_donation_disposal(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                            HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                            request.FILES.getlist('files'), request.user)

class AddTradeInDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        
        data = HelperMethods.json_str_to_dict(request.POST['data'])

        # Check if primary_vendor_email is missing or empty, and set a default value
        if not data.get('primary_vendor_email'):
            data['primary_vendor_email'] = 'default_primary_vendor_email@example.com'

        # Check if vendor_email is missing or empty, and set a default value
        if not data.get('vendor_email'):
            data['vendor_email'] = 'default_vendor_email@example.com'
        
        return DisposalHandler.handle_add_tradein_disposal(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                            HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                            request.FILES.getlist('files'), request.user)

class AddTransferDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_add_transfer_disposal(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                            HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                            request.FILES.getlist('files'), request.user)

class AddWriteOffDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_add_writeoff_disposal(HelperMethods.json_str_to_dict(request.POST['data']), 
                                                            HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                            request.FILES.getlist('files'), request.user)


# This view returns all asset disposals
class GetAssetDisposals(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_get_asset_disposals(request.user)


# This view returns all asset disposal writeoffs not associated with an accident
class GetAssetDisposalWriteOffNoAccident(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_get_asset_disposals_write_off_no_accident(request.user)


# This view returns asset disposal detail
class GetAssetDisposalDetailsByID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, disposal_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_get_asset_disposal_details_by_id(disposal_id, request.user)


# This view returns asset disposal detail
class GetAssetDisposalDetailsByCustomID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, custom_disposal_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_get_asset_disposal_details_by_custom_id(custom_disposal_id, request.user)


# Updates disposal fields
class UpdateDisposal(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_disposal(request.data, request.user)


# This view returns all asset disposal tradeins not associated with an asset request
class GetAssetDisposalTradeinNoAssetRequest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_get_asset_disposals_trade_in_no_asset_request(request.user)

        
# Updates company directed sale disposal status
class UpdateCompanyDirectedSaleDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_company_directed_sale_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                                    HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                                    request.FILES.getlist('files'), request.user)


# Updates auction disposal status
class UpdateAuctionDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_auction_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                        HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                        request.FILES.getlist('files'), request.user)


# Updates repurpose disposal status
class UpdateRepurposeDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_repurpose_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                        HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                        request.FILES.getlist('files'), request.user)


# Updates scrap disposal status
class UpdateScrapDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_scrap_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                    HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                    request.FILES.getlist('files'), request.user)


# Updates donation disposal status
class UpdateDonationDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_donation_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                        HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                        request.FILES.getlist('files'), request.user)


# Updates trade-in disposal status
class UpdateTradeInDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_trade_in_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                        HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                        request.FILES.getlist('files'), request.user)


# Updates transfer disposal status
class UpdateTransferDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_transfer_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                        HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                        request.FILES.getlist('files'), request.user)


# Updates write-off disposal status
class UpdateWriteOffDisposalStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return DisposalHandler.handle_update_write_off_disposal_status(HelperMethods.json_str_to_dict(request.POST['instructions']),
                                                                        HelperMethods.json_str_to_dict(request.POST['file_specs']), 
                                                                        request.FILES.getlist('files'), request.user)
