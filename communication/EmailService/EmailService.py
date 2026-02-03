from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from core.FileManager.FileInfo import FileInfo
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile, SimpleUploadedFile
import logging
import base64
from api.Models.Company import Company
from core.Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.mail import EmailMessage

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class Email:

    @staticmethod
    def send_email_notification(recipients, subject, content, files=[], html_content=False, archive=True, prepend_company=True):
        try:
            recipients = list(recipients)

            if archive:
                recipients.append(settings.ARCHIVE_EMAIL)

            if prepend_company:
                company_name = Company.objects.all().values_list('company_name', flat=True)[0]
                subject = str(company_name) + " " + subject

            if len(recipients) > 0:
                #print("html_content: " + content)
                print("from_email: " + str(settings.EMAIL_HOST_USER))
                print("to_email: " + str(recipients))
                print("subject: " + subject)
                print("Num of attachments: " + str(len(files)))
         
                # Build email 
                email = EmailMessage(
                    subject = subject,
                    body = content,
                    from_email = settings.EMAIL_HOST_USER,
                    to = recipients
                )

                # Attach files
                if len(files) > 0:

                    django_file_types = (InMemoryUploadedFile, TemporaryUploadedFile, SimpleUploadedFile)
                    custom_file_types = (FileInfo)

                    if HelperMethods.verify_obj_types(files, django_file_types):
                        email, attach_response = Email.attach_files_to_email_from_memory(files, email)
                        if attach_response.status_code != status.HTTP_200_OK:
                            return attach_response

                    elif HelperMethods.verify_obj_types(files, custom_file_types):
                        email, attach_response = Email.attach_files_to_email_from_disk(files, email)
                        if attach_response.status_code != status.HTTP_200_OK:
                            return attach_response

                    else:
                        print("Attachment file types were not recognized. Skipping attachments.")

                # Check if email content is html
                if html_content:
                    email.content_subtype = "html"

                # Send email
                email_status = email.send()

                # Check if email(s) sent (0 means fail)
                if email_status < 1:
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.EF_0, 'email.send() returned < 1'))
                    return Response(CustomError.get_full_error_json(CustomError.EF_0, 'email.send() returned < 1'), status=status.HTTP_400_BAD_REQUEST)
                
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.EF_0, e))
            return Response(CustomError.get_full_error_json(CustomError.EF_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def attach_files_to_email_from_disk(files, email):
        try:
            for file_info in files:
                with open(file_info.file_path, 'rb') as f:
                    data = f.read()
                    f.close()
                #encoded_file = base64.b64encode(data).decode()
                email.attach(file_info.file_name, data, file_info.file_type)
            return email, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.EF_1, e))
            return Response(CustomError.get_full_error_json(CustomError.EF_1, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def attach_files_to_email_from_memory(files, email):
        try:
            for f in files:
                f.open()
                email.attach(f.name, f.read(), f.content_type)
                f.close()
            return email, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.EF_1, e))
            return Response(CustomError.get_full_error_json(CustomError.EF_1, e), status=status.HTTP_400_BAD_REQUEST)
