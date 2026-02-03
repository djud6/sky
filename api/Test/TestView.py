from http import client
from pydoc import Helper
from api.Models.Cost.rental_cost import RentalCost
from api.Models.Cost.parts import Parts
from api.Models.Cost.labor_cost import LaborCost
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_file import AssetFile
from api.Models.asset_request import AssetRequestModel
from api.Models.asset_type_checks import AssetTypeChecks
from api.Models.repairs import RepairsModel
from core.ApprovalManager.ApprovalHelper import ApprovalHelper
from core.ApprovedVendorsManager.ApprovedVendorsHelper import ApprovedVendorsHelper
from core.AssetRequestManager.AssetRequestHelper import AssetRequestHelper
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from core.BusinessUnitManager.BusinessUnitHelper import BusinessUnitHelper
from core.ImportManager.EquipmentTypeImport import EquipmentTypeImport
from core.ImportManager.UserImport import UserImport
from core.MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from core.IssueManager.IssueHelper import IssueHelper
from core.RepairManager.RepairHelper import RepairHelper
from api.Models.equipment_type import EquipmentTypeModel
from api.Models.maintenance_request import MaintenanceRequestModel
import requests
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from communication.EmailService.EmailService import Email
from core.FileManager.PdfManager import PdfManager
from core.FileManager.FileInfo import FileInfo
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..Models.asset_issue import AssetIssueModel
from ..Models.asset_daily_checks import AssetDailyChecksModel
from ..Models.asset_manufacturer import AssetManufacturerModel
from ..Models.asset_model import AssetModel
from ..Models.asset_model_history import AssetModelHistory
from core.Helper import HelperMethods
from core.AssetManager.AssetHelper import AssetHelper
from core.UserManager.UserHelper import UserHelper
from core.UserManager.UserUpdater import UserUpdater
from core.DisposalManager.DisposalHelper import DisposalHelper
from core.TransferManager.TransferHelper import TransferHelper
from core.CompanyManager.CompanyHelper import CompanyHelper
from core.AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from core.RequestQuoteManager.RequestQuoteHandler import RequestQuoteHandler
from core.RequestQuoteManager.RequestQuoteHelper import RequestQuoteHelper
from core.RequestQuoteManager.RequestQuoteUpdater import RequestQuoteUpdater
from core.ImportManager.ManufacturerImport import ManufacturerImport
from django.core.files.uploadedfile import SimpleUploadedFile
from api.Models.Company import Company
from api.Serializers.serializers import (
    LightAssetRequestSerializer,
    AssetModelSerializer,
    LightIssueSerializer,
    SnapshotDailyLocationCostSerializerTest,
    RepairCostExportSerializer,
    MaintenanceCostExportSerializer,
)
import logging
import time
from datetime import datetime
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import asyncio
from asgiref.sync import sync_to_async
from multiprocessing.pool import ThreadPool
import time
import os
import json
from types import SimpleNamespace


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

# NOTE: This is to test out code while developing.
class TestView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(
                CustomError.get_full_error_json(CustomError.IT_0),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            db_name = request.user.db_access
            #----------------------------------TEST IN HERE-----------------------------------
            return Response(status=status.HTTP_200_OK)
            #---------------------------------------------------------------------------------
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )


# ---------------------------------------------------------------------------------------------------------------------

# NOTE: This is to test out code while developing.
class TestFormView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(
                CustomError.get_full_error_json(CustomError.IT_0),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            db_name = request.user.db_access
            files = request.FILES.getlist("files")
            # ----------------------------------TEST IN HERE-----------------------------------
            return Response(status=status.HTTP_200_OK)
            #---------------------------------------------------------------------------------
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )


# ---------------------------------------------------------------------------------------------------------------------

# NOTE: Do not alter to test code.
class TestServerConnection(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            return Response("Established contact with server!", status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

# ---------------------------------------------------------------------------------------------------------------------

# NOTE: Do not alter to test code.
class TestServerStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, status_code):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(
                CustomError.get_full_error_json(CustomError.IT_0),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if status_code == 200:
                return Response(status=status.HTTP_200_OK)
            elif status_code == 201:
                return Response(status=status.HTTP_201_CREATED)
            elif status_code == 202:
                return Response(status=status.HTTP_202_ACCEPTED)
            elif status_code == 400:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif status_code == 401:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            elif status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)

            return Response(
                "The provided status code is not currently supported by this API.",
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

# ---------------------------------------------------------------------------------------------------------------------

# NOTE: Do not alter to test code.
class LoadTest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            time.sleep(10)
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )


# ---------------------------------------------------------------------------------------------------------------------

# NOTE: Do not alter to test code.
class LoadTestAsync(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    async def get(self, request):
        await asyncio.sleep(10)
        return Response(status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------------------------------------------------

# NOTE: Do not alter to test code.
class ServerGatewayInterface(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            return Response(
                {"Interface": os.environ.get("SERVER_GATEWAY_INTERFACE")},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

# ---------------------------------------------------------------------------------------------------------------------

# NOTE: Do not alter to test code.
class TestMicroserviceConnection(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            return Response({"Interface": os.environ.get('SERVER_GATEWAY_INTERFACE')}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )
