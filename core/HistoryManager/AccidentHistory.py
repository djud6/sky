from rest_framework.response import Response
from rest_framework import status
from api.Models.accident_report_history import AccidentModelHistory
from api.Models.accident_report import AccidentModel
from api.Models.asset_log import AssetLog
from .AssetHistory import AssetHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AccidentHistory():

    @staticmethod
    def create_accident_report_record(accident_id, db_name):
        try:
            accident_report = AccidentModel.objects.using(db_name).get(accident_id=accident_id)
            accident_report_history_entry = AccidentHistory.generate_accident_report_history_entry(accident_report)
            accident_report_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_accident_report_record_by_obj(accident_report):
        try:
            accident_report_history_entry = AccidentHistory.generate_accident_report_history_entry(accident_report)
            accident_report_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_accident_report_history_entry(accident):
        return AccidentModelHistory(
            accident=accident,
            custom_id=accident.custom_id,
            estimated_return_date=accident.estimated_return_date,
            accident_report_completed=accident.accident_report_completed,
            is_equipment_failure=accident.is_equipment_failure,
            notification_ack=accident.notification_ack,
            evaluation_required=accident.evaluation_required,
            is_resolved=accident.is_resolved,
            is_preventable=accident.is_preventable,
            is_operational=accident.is_operational,
            date_returned_to_service=accident.date_returned_to_service,
            modified_by=accident.modified_by,
            accident_summary=accident.accident_summary,
            location=accident.location
        )

    @staticmethod
    def create_accident_event_log(accident_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(accident_obj.VIN, AssetLog.accident, accident_obj.custom_id, accident_obj.modified_by, description, accident_obj.location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_3, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_3, e), status=status.HTTP_400_BAD_REQUEST)
