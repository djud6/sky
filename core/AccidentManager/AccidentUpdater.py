from rest_framework.response import Response
from rest_framework import status
from api.Models.accident_report import AccidentModel
from api.Models.accident_file import AccidentFileModel
from .AccidentHelper import AccidentHelper
from api.Models.DetailedUser import DetailedUser
from ..UserManager.UserHelper import UserHelper
from ..Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AccidentUpdater():

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_accident_post_creation(accident_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            accident_obj.created_by = detailed_user
            accident_obj.modified_by = detailed_user
            accident_obj.custom_id = str(detailed_user.company.company_name).replace(' ', '-') + '-a-' + str(accident_obj.accident_id)
            accident_obj.save()
            return accident_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_0, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def create_accident_file_record(accident_obj, file_infos, db_name):
        try:
            entries = list()
            for file_info in file_infos:
                entries.append(AccidentUpdater.construct_accident_file_model_instance(accident_obj, file_info))
            AccidentFileModel.objects.using(db_name).bulk_create(entries)
    
            return True
        
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    # --------------------------------------------------------------------------------------

    @staticmethod
    def construct_accident_file_model_instance(accident_obj, file_info):
        return AccidentFileModel(
            accident=accident_obj,
            file_type=file_info.file_type,
            file_name=file_info.file_name,
            file_url=file_info.file_url,
            bytes=file_info.bytes
        )
    
    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_accident_modified_by(accident_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            accident_obj.modified_by = detailed_user
            accident_obj.save()
            return accident_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_0, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_accident_fields(accident_entry, request_data, user):
        try:
            is_important = False
            if not len(str(request_data.get("accident_report_completed"))) == 0 and request_data.get("accident_report_completed") is not None:
                accident_entry.accident_report_completed = HelperMethods.validate_bool(request_data.get("accident_report_completed"))
            if not len(str(request_data.get("is_equipment_failure"))) == 0 and request_data.get("is_equipment_failure") is not None:
                accident_entry.is_equipment_failure = HelperMethods.validate_bool(request_data.get("is_equipment_failure"))
            if not len(str(request_data.get("notification_ack"))) == 0 and request_data.get("notification_ack") is not None:
                accident_entry.notification_ack = HelperMethods.validate_bool(request_data.get("notification_ack"))
            if not len(str(request_data.get("evaluation_required"))) == 0 and request_data.get("evaluation_required") is not None:
                accident_entry.evaluation_required = HelperMethods.validate_bool(request_data.get("evaluation_required"))
            if not len(str(request_data.get("is_resolved"))) == 0 and request_data.get("is_resolved") is not None:
                accident_entry.is_resolved = HelperMethods.validate_bool(request_data.get("is_resolved"))
            if not len(str(request_data.get("is_preventable"))) == 0 and request_data.get("is_preventable") is not None:
                accident_entry.is_preventable = HelperMethods.validate_bool(request_data.get("is_preventable"))
            if not len(str(request_data.get("is_operational"))) == 0 and request_data.get("is_operational") is not None:
                accident_entry.is_operational = HelperMethods.validate_bool(request_data.get("is_operational"))
            if not len(str(request_data.get("accident_summary"))) == 0 and request_data.get("accident_summary") is not None:
                accident_entry.accident_summary = request_data.get("accident_summary").strip()
            if not len(str(request_data.get("estimated_return_date"))) == 0 and request_data.get("estimated_return_date") is not None:
                accident_entry.estimated_return_date = HelperMethods.datetime_string_to_datetime(request_data.get("estimated_return_date"))
                is_important = True
            if not len(str(request_data.get("date_returned_to_service"))) == 0 and request_data.get("date_returned_to_service") is not None:
                accident_entry.date_returned_to_service = HelperMethods.datetime_string_to_datetime(request_data.get("date_returned_to_service"))

            accident_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            return accident_entry, is_important, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.TUF_5, e)
            return None, is_important, Response(CustomError.get_full_error_json(CustomError.TUF_5, e), status=status.HTTP_400_BAD_REQUEST)