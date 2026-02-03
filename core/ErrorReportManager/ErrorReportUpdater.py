from rest_framework.response import Response
from rest_framework import status
from ..UserManager.UserHelper import UserHelper
from api.Models.error_report import ErrorReport
from api.Models.error_report_file import ErrorReportFile
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class ErrorReportUpdater():

    @staticmethod
    def create_error_report(error_report_data, user):
        try:
            sender_detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            error_report_entry = ErrorReportUpdater.create_error_report_entry(error_report_data, user, sender_detailed_user)
            error_report_entry.save()
            return error_report_entry, Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_error_report_entry(request_data, user, sender_detailed_user):
        return ErrorReport(
            issue_type=request_data.get("issue_type"),
            error_title=request_data.get("error_title"),
            error_description=request_data.get("error_description"),
            steps_to_reproduce=request_data.get("steps_to_reproduce"),
            created_by=sender_detailed_user
        )

    @staticmethod
    def create_error_report_file_record(error_report_obj, file_infos, dbName):
        try:
            entries = list()
            for file_info in file_infos:
                entries.append(ErrorReportUpdater.construct_error_report_file_entry(error_report_obj, file_info))
            ErrorReportFile.objects.using(dbName).bulk_create(entries)

            return True
        
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def construct_error_report_file_entry(error_report_obj, file_info):
        return ErrorReportFile(
            error_report=error_report_obj,
            file_type=file_info.file_type,
            file_name=file_info.file_name,
            file_url=file_info.file_url,
            bytes=file_info.bytes
        )