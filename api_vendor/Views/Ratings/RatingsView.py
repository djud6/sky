from urllib import request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.RatingsManager.RatingsHandler import RatingsHandler
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.UserManager.UserHelper import UserHelper
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


class AddRating(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return RatingsHandler.handle_add_vendor_rating(request.data, request.user)


# INBOUND ------------------------------------------------------------------------------------

"""
    APIs that process requests internally go here.
"""
