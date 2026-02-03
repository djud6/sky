from rest_framework import status
from api.Models.asset_request import AssetRequestModel
from api.Models.asset_request_history import AssetRequestModelHistory
import logging


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetRequestHistory:
    @staticmethod
    def create_asset_request_record(asset_request_id, db_name):
        try:
            asset_request = AssetRequestModel.objects.using(db_name).get(pk=asset_request_id)
            asset_request_history_entry = AssetRequestHistory.generate_asset_request_history_entry(asset_request)
            asset_request_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_asset_request_record_by_obj(asset_request):
        try:
            asset_request_history_entry = AssetRequestHistory.generate_asset_request_history_entry(asset_request)
            asset_request_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_asset_request_history_entry(asset_request):
        return AssetRequestModelHistory(
            asset_request=asset_request,
            custom_id=asset_request.custom_id,
            business_unit=asset_request.business_unit,
            equipment_id=asset_request.equipment_id,
            date_required=asset_request.date_required,
            estimated_delivery_date=asset_request.estimated_delivery_date,
            justification=asset_request.justification,
            nonstandard_description=asset_request.nonstandard_description,
            vendor_email=asset_request.vendor_email,
            modified_by=asset_request.modified_by,
            status=asset_request.status,
            vendor=asset_request.vendor,
            location=asset_request.location,
            VIN=asset_request.VIN,
            quantity=asset_request.quantity
        )
