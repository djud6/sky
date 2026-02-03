from rest_framework.response import Response
from rest_framework import status
from api.Models.repairs_history import RepairsModelHistory
from api.Models.repairs import RepairsModel
from api.Models.asset_log import AssetLog
from .AssetHistory import AssetHistory
from ..AssetManager.AssetHelper import AssetHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RepairHistory():

    @staticmethod
    def create_repair_record(repair_id, db_name):
        try:
            repair = RepairsModel.objects.using(db_name).get(repair_id=repair_id)
            repair_history_entry = RepairHistory.generate_repairhistory_entry(repair)
            repair_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_repair_record_by_obj(repair, db_name):
        try:
            repair_history_entry = RepairHistory.generate_repairhistory_entry(repair)
            repair_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_repairhistory_entry(repair):
        return RepairsModelHistory(
            repair = repair,
            work_order = repair.work_order,
            vendor = repair.vendor,
            location = repair.location,
            description = repair.description,
            requested_delivery_date = repair.requested_delivery_date,
            estimated_delivery_date = repair.estimated_delivery_date,
            available_pickup_date = repair.available_pickup_date,
            date_completed = repair.date_completed,
            down_time = repair.down_time,
            vendor_contacted_date = repair.vendor_contacted_date,
            vendor_email = repair.vendor_email,
            mileage = repair.mileage,
            hours = repair.hours,
            modified_by=repair.modified_by,
            status = repair.status
        )

    @staticmethod
    def create_repair_event_log(repair_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(repair_obj.VIN, AssetLog.repair, repair_obj.work_order, repair_obj.modified_by, description, repair_obj.location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_1, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_1, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def batch_history_and_logs_for_asset_status_change_by_repair(repair_qs, status_update, db_name):
        # The `iterator()` method ensures only a few rows are fetched from
        # the database at a time, saving memory.
        for repair in repair_qs.iterator():
            # create asset history record
            print("Updating status for " + str(repair.VIN) + " in db (" + str(db_name) + ")")
            asset_obj = AssetHelper.get_asset_by_VIN(repair.VIN, db_name)
            if(not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Asset was set to " + str(status_update) + " due to repair " + str(repair.work_order)
            event_log_response = RepairHistory.create_repair_event_log(repair, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

        return Response(status=status.HTTP_201_CREATED)
        