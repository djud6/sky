from django import db
from rest_framework.response import Response
from rest_framework import status
from api.Models.approved_vendors import ApprovedVendorsModel
from api.Models.repairs import RepairsModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_request import AssetRequestModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class VendorHelper():

    @staticmethod
    def get_vendor_by_id(vendor_id, db_name):
        try:
            return ApprovedVendorsModel.objects.using(db_name).get(vendor_id=vendor_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.VIDDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.VIDDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_vendor_by_email(vendor_email, db_name):
        try:
            return ApprovedVendorsModel.objects.using(db_name).get(primary_email=vendor_email), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.VIDDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.VIDDNE_0, e), status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def get_repairs_for_vendor_by_email(vendor_email, db_name):
        try:
            return RepairsModel.objects.using(db_name).filter(vendor_email = vendor_email)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_maintenance_for_vendor_by_email(vendor_email, db_name):
        try:
            return MaintenanceRequestModel.objects.using(db_name).filter(vendor_email = vendor_email)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_disposal_for_vendor_by_email(vendor_email, db_name):
        try:
            return AssetDisposalModel.objects.using(db_name).filter(primary_vendor_email = vendor_email)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_asset_requests_for_vendor_by_email(vendor_email, db_name):
        try:
            return AssetRequestModel.objects.using(db_name).filter(vendor_email = vendor_email)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_repair_status(repair_id, db_name):
        try:
            repair_obj = RepairsModel.objects.using(db_name).get(repair_id = repair_id)
            repair_obj.status = "complete"
            repair_obj.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_maintenance_status(maintenance_id, db_name):
        try:
            maintenance_obj = MaintenanceRequestModel.objects.using(db_name).get(maintenance_id = maintenance_id)
            maintenance_obj.status = "complete"
            maintenance_obj.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_asset_request_status(asset_id, db_name):
        try:
            asset_obj = AssetRequestModel.objects.using(db_name).get(pk = asset_id)
            asset_obj.status = "in transit"
            asset_obj.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
