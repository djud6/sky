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
from api.Models.asset_model_history import AssetModelHistory
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
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.ImportManager.ManufacturerImport import ManufacturerImport
from api_vendor.Auth.AuthHelper import AuthHelper
from django.core.files.uploadedfile import SimpleUploadedFile
from api.Models.Company import Company
from api.Models.asset_model import AssetModel
from api.Serializers.serializers import (
    LightAssetRequestSerializer,
    AssetModelSerializer,
    LightIssueSerializer,
    SnapshotDailyLocationCostSerializerTest,
    RepairCostExportSerializer,
    MaintenanceCostExportSerializer,
    JobSpecificationSerializer
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

from rest_framework_api_key.permissions import HasAPIKey

class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

# OUTBOUND -----------------------------------------------------------------------------------

"""
    APIs that send out requests to the main system go here.
"""

class TestClientRouting(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)   

    def get(self, request):
        try:
            vendor_name = "Vendor Company"
            VendorOpsHelper.get_vendor_data("TestClientRouting/" + str(vendor_name), {})
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

# INBOUND ------------------------------------------------------------------------------------

"""
    APIs that process requests internally go here.
"""

class TestConnectionFromVendorServer(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            if not AuthHelper.authenticate_vendor_request(request):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
                
            return Response({"message": "authenticated with api key"}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )


class TestVendorRouting(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        try:
            if not AuthHelper.authenticate_vendor_request(request):
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            assets = AssetModel.objects.all()
            print(assets)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )
