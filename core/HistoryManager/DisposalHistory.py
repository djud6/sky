from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_disposal_history import AssetDisposalModelHistory
from api.Models.asset_log import AssetLog
from .AssetHistory import AssetHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DisposalHistory:

    @staticmethod
    def create_asset_disposal_record(_id, db_name):
        try:
            asset_disposal = AssetDisposalModel.objects.using(db_name).get(pk=_id)
            asset_disposal_history_entry = DisposalHistory.generate_asset_disposal_history_entry(asset_disposal)
            asset_disposal_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_asset_disposal_record_by_obj(asset_disposal, db_name):
        try:
            asset_disposal_history_entry = DisposalHistory.generate_asset_disposal_history_entry(asset_disposal)
            asset_disposal_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_asset_disposal_history_entry(asset_disposal):
        return AssetDisposalModelHistory(
            disposal=asset_disposal,
            custom_id=asset_disposal.custom_id,
            status=asset_disposal.status,
            vendor=asset_disposal.vendor,
            disposal_type=asset_disposal.disposal_type,
            estimated_pickup_date=asset_disposal.estimated_pickup_date,
            vendor_contacted_date=asset_disposal.vendor_contacted_date,
            accounting_contacted_date=asset_disposal.accounting_contacted_date,
            available_pickup_date=asset_disposal.available_pickup_date,
            modified_by=asset_disposal.modified_by,
            location=asset_disposal.location
        )

    @staticmethod
    def create_asset_disposal_event_log(disposal_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(disposal_obj.VIN, AssetLog.disposal, disposal_obj.custom_id, disposal_obj.modified_by, description, disposal_obj.location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_7, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_7, e), status=status.HTTP_400_BAD_REQUEST)