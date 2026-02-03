from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_transfer_history import AssetTransferModelHistory
from api.Models.asset_transfer import AssetTransfer
from api.Models.asset_log import AssetLog
from .AssetHistory import AssetHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class TransferHistory():

    @staticmethod
    def create_transfer_record(asset_transfer_id, db_name):
        try:
            asset_transfer = AssetTransfer.objects.using(db_name).get(asset_transfer_id=asset_transfer_id)
            transfer_history_entry = TransferHistory.generate_transfer_history_entry(asset_transfer)
            transfer_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_transfer_record_by_obj(asset_transfer):
        try:
            transfer_history_entry = TransferHistory.generate_transfer_history_entry(asset_transfer)
            transfer_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_transfer_history_entry(asset_transfer):
        return AssetTransferModelHistory(
            asset_transfer = asset_transfer,
            custom_id=asset_transfer.custom_id,
            original_location = asset_transfer.original_location,
            destination_location = asset_transfer.destination_location,
            disposal = asset_transfer.disposal,
            justification = asset_transfer.justification,
            status = asset_transfer.status,
            pickup_date = asset_transfer.pickup_date,
            modified_by = asset_transfer.modified_by,
            longitude = asset_transfer.longitude,
            latitude = asset_transfer.latitude,
            interior_condition = asset_transfer.interior_condition,
            interior_condition_details = asset_transfer.interior_condition_details,
            exterior_condition = asset_transfer.exterior_condition,
            exterior_condition_details = asset_transfer.exterior_condition_details,
            mileage = asset_transfer.mileage,
            hours = asset_transfer.hours
        )

    @staticmethod
    def create_asset_transfer_event_log(transfer_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(transfer_obj.VIN, AssetLog.transfer, transfer_obj.custom_id, transfer_obj.modified_by, description, transfer_obj.original_location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_9, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_9, e), status=status.HTTP_400_BAD_REQUEST)