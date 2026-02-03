from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api_ghg.Auth.AuthHelper import AuthHelper
from api.Models.Company import Company

from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

# OUTBOUND -----------------------------------------------------------------------------------

"""
    APIs that send out requests to the main system go here.
"""


# INBOUND ------------------------------------------------------------------------------------

"""
    APIs that process requests internally go here.
"""

class TestConnectionToClientServer(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            if not AuthHelper.authenticate_ghg_request(request):
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            mock_data = {
                "data_point_1": "data_1",
                "data_point_2": "data_2",
                "data_point_3": "data_3"
            }

            return Response(mock_data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )


class TestRoutingToClientServer(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        try:
            if not AuthHelper.authenticate_ghg_request(request):
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            company = Company.objects.all()[0]

            data = {
                "routed_to": company.company_name
            }

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )
