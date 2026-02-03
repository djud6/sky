from rest_framework.response import Response
from rest_framework import status
from api.Models.DetailedUser import DetailedUser
from .ErrorReportHelper import ErrorReportHelper
from .ErrorReportUpdater import ErrorReportUpdater
from ..FileManager.FileHelper import FileHelper
from ..FileManager.PdfManager import PdfManager
from communication.EmailService.EmailService import Email
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.conf import settings
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ErrorReportHandler():

    @staticmethod
    def handle_create_error_report(request_data, images, user):

        try:
            # Check issue type validity
            if not ErrorReportHelper.is_issue_type_valid(request_data.get("issue_type")):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IER_0))
                return Response(CustomError.get_full_error_json(CustomError.IER_0), status=status.HTTP_400_BAD_REQUEST)

            # Create error report
            error_report_obj, entry_response = ErrorReportUpdater.create_error_report(request_data, user)
            if entry_response.status_code != status.HTTP_201_CREATED:
                return entry_response

            # -------------- Verify file types ---------------
            valid_issue_file_types = ["image/jpeg", "image/png", "image/heic", "image/heif"]
            if(not FileHelper.verify_files_are_accepted_types(images, valid_issue_file_types)):
                error_report_obj.delete()
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_1))
                return Response(CustomError.get_full_error_json(CustomError.IUF_1), status=status.HTTP_400_BAD_REQUEST)

            # ------------ Upload files to blob --------------
            company = DetailedUser.objects.get(email=user.email).company
            company_name = company.company_name
            file_suffix = "Error_Report_" + str(error_report_obj.error_report_id) + "_"
            image_status, file_infos = BlobStorageHelper.write_files_to_blob(images, "feedback", file_suffix, company_name, user.db_access)
            if(not image_status):
                error_report_obj.delete()
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)

            # ----------- Upload file urls to DB --------------
            if(not ErrorReportUpdater.create_error_report_file_record(error_report_obj, file_infos, user.db_access)):
                error_report_obj.delete()
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)

            # -------------- Email issue report ---------------
            software_name = company.software_name
            html_message = PdfManager.gen_error_report_html(error_report_obj, user)
            email_title = "User Feedback Report (ID " + str(error_report_obj.error_report_id) + ")"
            support_email = ErrorReportHelper.find_support_email(software_name)
            recipients = [user.email, support_email]
            
            email_response = Email.send_email_notification(recipients, email_title, html_message, images, html_content=True)

            if email_response.status_code != status.HTTP_200_OK:
                return email_response
            # -------------------------------------------------

            return Response(status=status.HTTP_201_CREATED)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
