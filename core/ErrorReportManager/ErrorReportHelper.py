from django.core.mail.message import sanitize_address
from rest_framework.response import Response
from rest_framework import status
from api.Models.error_report import ErrorReport
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from django.conf import settings
from api.Models.error_report_file import ErrorReportFile
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ErrorReportHelper():

    @staticmethod
    def select_related_to_error_report(queryset):
        return queryset.select_related('created_by')

    @staticmethod
    def get_error_report_ser_context(db_name):
        container_name = "feedback"
        feedback_files = ErrorReportFile.objects.using(db_name).all().values()
        for asset in feedback_files:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, container_name, asset.get('file_url'))
            asset['file_url'] = secure_file_url
        return {
            'all_files': feedback_files
            }

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def is_issue_type_valid(issue_type):
        if issue_type in dict(ErrorReport.issue_type_choices):
            return True
        return False

    @staticmethod
    def find_support_email(software_name):
        email_dict = {
            "unknown" : settings.EMAIL_HOST_USER,
            "aukai" : settings.AUKAI_SUPPORT_EMAIL,
            "orion" : settings.ORION_SUPPORT_EMAIL,
            "lokomotive" : settings.LOKOMOTIVE_SUPPORT_EMAIL
        }

        return email_dict[software_name]
