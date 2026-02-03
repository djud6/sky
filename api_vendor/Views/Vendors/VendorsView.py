from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from api_vendor.Auth.AuthHelper import AuthHelper
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from api.Models.approved_vendors import ApprovedVendorsModel
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.ApprovedVendorsManager.ApprovedVendorsHandler import ApprovedVendorsHandler
from core.UserManager.UserHelper import UserHelper
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

class AddClientConnectionRequest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, vendor_name):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        try:
            db_name = request.user.db_access
            client_company = UserHelper.get_detailed_user_obj(request.user.email, db_name).company
            payload = {
                "vendor_name": vendor_name,
                "client_name": client_company.company_name,
                "client_address": client_company.company_address,
                "client_phone": client_company.company_phone
            }

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Connection/Request/Add/" + str(vendor_name), payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )  

class ListAllAvailableVendor(APIView):
    
    def get(self, request):
        result = ApprovedVendorsHandler.handle_get_all_available_vendors()
        return Response(result, status=status.HTTP_200_OK)

# INBOUND ------------------------------------------------------------------------------------

"""
    APIs that process requests internally go here.
"""

class UpdateVendorRatingsForAllClients(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = HelperMethods.json_str_to_dict(request.POST["data"])
            vendor_ratings_data = data.get("vendor_ratings")
            database_names = list(settings.DATABASES.keys())

            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    print("--------------------")
                    print(db_name)
                    print("--------------------")

                    with transaction.atomic():
                        for key, value in vendor_ratings_data.items():
                            try:
                                ApprovedVendorsModel.objects.using(db_name).filter(vendor_name=key).update(rating=value)
                                print("Vendor rating updated - Key: " + str(key) + " // Value: " + str(value))
                            except Exception as e:
                                print("Skipping vendor rating:")
                                print(e)

                else:
                    print("Skipping " + db_name + "...")

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

    
class AddApprovedVendor(APIView):
    permission_classes = [AllowAny]

    def post(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            return ApprovedVendorsHandler.handle_add_approved_vendor(request.data)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateVendorServices(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = HelperMethods.json_str_to_dict(request.POST["data"])
            return ApprovedVendorsHandler.handle_update_vendor_services(data)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )
