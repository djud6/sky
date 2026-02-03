from rest_framework.response import Response
from rest_framework import status
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class RatingsHandler():

    @staticmethod
    def handle_add_vendor_rating(request_data, user):
        try:
            client_name = UserHelper.get_company_name_by_user_email(
                user.email, user.db_access
            )

            body = {
                **request_data,
                **{
                    "client_name": client_name,
                    "vendor_name": request_data.get("vendor_name"),
                },
            }

            res = VendorOpsHelper.post_vendor_data(
                "Client/Ratings/Add/" + str(request_data.get("vendor_name")),
                body
            )
            if res.status_code != status.HTTP_200_OK:
                return res
            
            return Response(res.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )