from rest_framework.response import Response
from rest_framework import status
from api_auth.Serializers.serializers import (
    UserConfigurationSerializer,
    UserModelSerializer,
    DetailedSuperUserSerializer,
    LinkedSuperUserModelSerializer,
    DetailedUserSerializer,
    RolePermissionsSerializer
    )
from api_auth.Auth_User.user_manager import UserManager
from .UserHelper import UserHelper
from .UserUpdater import UserUpdater
from core.HistoryManager.UserHistory import UserHistory
from core.HistoryManager.DetailedUserHistory import DetailedUserHistory
from core.FileManager.PdfManager import PdfManager
from core.RolePermissionsManager.RolePermissionsHelper import RolePermissionsHelper
from core.Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
from communication.EmailService.EmailService import Email
from api_auth.Auth_User.User import User
import logging
from api_auth.Auth_User.db_constants import Constants
from rest_framework.authtoken.models import Token
# New Forgot Password packages
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponsePermanentRedirect
import os
from django.urls import base, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from api.Models.locations import LocationModel
import ast
class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class UserHandler():

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_users(user):
        try:
            if user.is_superuser:
                emails = list(UserHelper.get_all_active_users_for_company(user.db_access).values_list('email', flat=True))
                all_detailed_users = UserHelper.get_detailed_users_by_emails(emails, user.db_access)
                ser = DetailedUserSerializer(all_detailed_users, many=True)
                return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_role_permissions(user):
        try:
            if user.is_superuser:
                all_role_permissions = RolePermissionsHelper.get_all_role_permissions(user.db_access)
                ser = RolePermissionsSerializer(all_role_permissions, many=True)
                return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_create_user(request_data, user):
        try:
            # Check if requesting user is superuser
            if not user.is_superuser:
                Logger.getLogger().error(CustomError.UNSU_0)
                return Response(CustomError.get_full_error_json(CustomError.UNSU_0), status=status.HTTP_400_BAD_REQUEST)

            # Verify email is not already in use by someone in system
            if UserHelper.email_user_entry_exists(request_data.get("email")):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IE_1))
                return Response(CustomError.get_full_error_json(CustomError.IE_1), status=status.HTTP_400_BAD_REQUEST)
            
            # Check if foreign keys provided exist
            fkeys_response = UserHelper.user_foreign_keys_exist(request_data, user)
            if fkeys_response.status_code != status.HTTP_200_OK:
                return fkeys_response

            email = request_data.get("email")
            first_name = request_data.get("first_name")
            last_name = request_data.get("last_name")

            # Creating a password for the user
            password = UserHelper.generate_random_password()

            # Create user
            user_obj = User.objects.create_user(email, password, user.db_access,
            first_name=first_name, 
            last_name=last_name)

            # Create detailed user
            detailed_user_obj, detailed_user_response = UserUpdater.create_detailed_user(request_data, user.email, user.db_access)
            if detailed_user_response.status_code != status.HTTP_201_CREATED:
                return detailed_user_response

            # Create user configuration entry
            user_config, user_config_response = UserUpdater.create_user_configuration(detailed_user_obj)
            if user_config_response.status_code != status.HTTP_201_CREATED:
                return user_config_response
                
            # Create user record
            if(not UserHistory.create_user_record(user_obj.id)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)

            # Create detailed user record
            if(not DetailedUserHistory.create_detailed_user_record(detailed_user_obj.detailed_user_id, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)

            # Send email to user with account details
            # -------------- Email user info ---------------
            html_content = PdfManager.gen_new_account_html(user_obj, password)
            email_title = "Your " + str(detailed_user_obj.company.software_name).capitalize() + " Account"
            recipients = [user_obj.email]
            email_response = Email.send_email_notification(recipients, email_title, html_content, html_content=True)
            if email_response.status_code != status.HTTP_200_OK:
                return email_response

            return Response(UserModelSerializer(user_obj).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_user_locations(request_data, user):
        try:
            user_location_entries = []
            locations = request_data.get("location_ids")
            user_id = UserHelper.get_detailed_user_id_by_email(request_data.get("email"), user.db_access)
            for location_id in locations:
                if not UserHelper.user_location_exists(user_id, location_id, user.db_access):
                    entry = UserUpdater.create_user_location_entry(user_id, location_id)
                    user_location_entries.append(entry)

            UserUpdater.user_location_bulk_create(user_location_entries, user.db_access)
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_user_locations(request_data, user):
        try:
            user_location_entries = []
            locations = request_data.get("location_ids")
            user_id = UserHelper.get_detailed_user_id_by_email(request_data.get("email"), user.db_access)
            location_list = []
            is_deleted = True
            for location_id in locations:
                if UserHelper.location_id_exists(location_id, user.db_access):
                    if is_deleted:
                        delete_locations = UserHelper.delete_locations_by_user_detailed_user_id(user_id, user.db_access)
                        is_deleted = False
                    location_list.append(location_id)
            if not location_list:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            for location_id in location_list:
                if not UserHelper.user_location_exists(user_id, location_id, user.db_access):
                    entry = UserUpdater.create_user_location_entry(user_id, location_id)
                    user_location_entries.append(entry)
            UserUpdater.user_location_bulk_create(user_location_entries, user.db_access)
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_user_password(request_data, user):

        try:
            # Check if password is valid
            pass_response = UserHelper.validate_password(request_data.get("password"))
            if(not pass_response.status_code == status.HTTP_200_OK):
                return pass_response

            # Update password
            UserUpdater.update_user_password(user, request_data.get("password"))
            token = Token.objects.using(Constants.AUTH_DB).get(user=user)
            token.delete()

            # Create user record
            if(not UserHistory.create_user_record(user.id)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)

            # Check to see if this is user's first login --> if it is mark first_time_login
            # as False since user has changed password.
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            if detailed_user.first_time_login:
                detailed_user.first_time_login = False
                detailed_user.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
            
    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_forgot_password(self, request):

        try:
            email = request.data.get("email")

            # Check if account exists with given email
            if UserHelper.email_user_entry_exists(email):
                user = User.objects.using(UserHelper.auth_db_name).get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(
                    request=request).domain
                relative_link = reverse(
                    'api_auth:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
                company_obj = UserHelper.get_company_obj_by_user_email(email, user.db_access)
                software_name = str(company_obj.software_name).lower()
                base_url = settings.FORGOT_PASSWORD_URL.get(software_name)
                redirect_url = request.data.get('redirect_url', base_url)
                absurl = 'http://'+current_site + relative_link
                email_title = str(company_obj.company_name) + " " + software_name.capitalize() + " Account Password Reset"
                reset_url = absurl + "?redirect_url=" + redirect_url +'/request-new-password'
                html_content = PdfManager.gen_reset_password_html(reset_url, user)

                email_response = Email.send_email_notification([email], email_title, html_content, html_content=True, prepend_company=False)
                if email_response.status_code != status.HTTP_200_OK:
                    return email_response

            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IL_1))
                return Response(CustomError.get_full_error_json(CustomError.IL_1), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
            
    # -------------------------------------------------------------------------------------------------------------------
            
    @staticmethod
    def handle_forgot_password_token_check(self, request, uidb64, token):
        try:
            redirect_url = request.GET.get('redirect_url')
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.using(UserHelper.auth_db_name).get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
                return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user, token):
                    return CustomRedirect(redirect_url+'?token_valid=False')
            except UnboundLocalError as e:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
                return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_forgot_password_generate(self, request):
        
        token = request.data.get("token")        
        uidb64 = request.data.get("uidb64")        
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.using(UserHelper.auth_db_name).get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
                return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
                
            if not UserHelper.email_user_entry_exists(user.email):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IL_1))
                return Response(CustomError.get_full_error_json(CustomError.IL_1), status=status.HTTP_400_BAD_REQUEST)
            # Generate password
            password = UserHelper.generate_random_password()

            # Email password to user
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            detailed_user.first_time_login = True
            detailed_user.save()
            html_content = PdfManager.gen_temp_password_html(password, user)
            email_title = "Your " + str(detailed_user.company.software_name).capitalize() + " Account Password Has Changed"
            email_response = Email.send_email_notification([user.email], email_title, html_content, html_content=True, prepend_company=False)
            if email_response.status_code != status.HTTP_200_OK:
                return email_response
            # Update password
            user_obj = UserHelper.get_user_obj_by_email(user.email)
            UserUpdater.update_user_password(user_obj, password)

            # Create user record
            if(not UserHistory.create_user_record(user_obj.id)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_edit_user_account(request_data, user):

        try:
            db_name = user.db_access

            # Verify that user exists for provided id
            if not UserHelper.id_user_entry_exists(request_data.get("user_id")):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)

            if request_data.get("email") is not None:
                # Verify that email is valid
                email_valid, email_validity_msg = HelperMethods.verify_email_address(request_data.get("email"))
                if not email_valid:
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.IE_0, email_validity_msg))
                    return Response(CustomError.get_full_error_json(CustomError.IE_0, email_validity_msg), status=status.HTTP_400_BAD_REQUEST)

                # Verify email is not already in use by someone in system
                if UserHelper.email_user_entry_exists(request_data.get("email")):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.IE_1))
                    return Response(CustomError.get_full_error_json(CustomError.IE_1), status=status.HTTP_400_BAD_REQUEST)

            # Check if foreign keys provided exist
            fkeys_response = UserHelper.user_foreign_keys_exist(request_data, user)
            if fkeys_response.status_code != status.HTTP_200_OK:
                return fkeys_response

            # Update the user account entry
            user_obj = UserHelper.get_user_obj(request_data.get("user_id"))
            detailed_user_obj = UserHelper.get_detailed_user_obj(user_obj.email, db_name)
            user_obj, detailed_user_obj, exception_text = UserUpdater.update_user_account(user_obj, detailed_user_obj, request_data, db_name)
            if user_obj is None or detailed_user_obj is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UUF_0, exception_text))
                return Response(CustomError.get_full_error_json(CustomError.UUF_0, exception_text), status=status.HTTP_400_BAD_REQUEST)

            # Create user record
            if(not UserHistory.create_user_record(request_data.get("user_id"))):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)
            # Create detailed user record
            if(not DetailedUserHistory.create_detailed_user_record(detailed_user_obj.detailed_user_id, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    # need to check who the requesting user is. If they are the superusers
    # request data with previous email-id in the body along with the update emailID and all the other information
    @staticmethod
    def handle_get_any_user_information(request_data, user):

        try:
            if not user.is_superuser:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UNSU_0))
                return Response(CustomError.get_full_error_json(CustomError.UNSU_0), status=status.HTTP_403_FORBIDDEN)
            if not UserHelper.email_user_entry_exists(request_data.get("email")):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)

            user_Info = UserHelper.get_user_by_email(request_data.get("email"))
            # If the user access of SU and requested email is not same, return UDNE
            if user_Info.db_access != user.db_access:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)
            detailed_user_info = UserHelper.get_detailed_user_obj(request_data.get("email"), user_Info.db_access)
            user_config = UserHelper.get_user_config_by_user_id(detailed_user_info.detailed_user_id, user.db_access)
            if not user_Info == status.HTTP_404_NOT_FOUND:
                user_serializer = LinkedSuperUserModelSerializer(user_Info)
                detailed_user_serializer = DetailedSuperUserSerializer(detailed_user_info)
                user_config_serializer = UserConfigurationSerializer(user_config)
                return Response({"user": user_serializer.data,
                "detailed_user": detailed_user_serializer.data,
                'user_config': user_config_serializer.data},
                status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    # need to check who the requesting user is. If they are the superusers
    # request data with previous email-id in the body along with the update emailID and all the other information
    @staticmethod
    def handle_edit_any_user_account(request_data, user):

        try:
            if not user.is_superuser:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UNSU_0))
                return Response(CustomError.get_full_error_json(CustomError.UNSU_0), status=status.HTTP_403_FORBIDDEN)
            # Verify that user exists for provided id
            if not UserHelper.id_user_entry_exists(request_data.get("user_id")):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)

            if not UserHelper.email_user_entry_exists(request_data.get("email")):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)

            user_obj = UserHelper.get_user_obj(request_data.get("user_id"))
            # If the user access of SU and requested email is not same, return UDNE
            if user_obj.db_access != user.db_access:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)
            # Update the user account entry
            detailed_user_obj = UserHelper.get_detailed_user_obj(user_obj.email, user_obj.db_access)
            user_obj, detailed_user_obj, exception_text = UserUpdater.update_user_account(user_obj, detailed_user_obj, request_data, user_obj.db_access)
            if user_obj is None or detailed_user_obj is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UUF_0, exception_text))
                return Response(CustomError.get_full_error_json(CustomError.UUF_0, exception_text), status=status.HTTP_400_BAD_REQUEST)
            locations = UserHandler.handle_update_user_locations(request_data, user_obj)
            if locations.status_code != 201:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.LDE_0))
                return Response(CustomError.get_full_error_json(CustomError.LDE_0), status=status.HTTP_400_BAD_REQUEST)
            # Create user record
            if(not UserHistory.create_user_record(request_data.get("user_id"))):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)
            # Create detailed user record
            if(not DetailedUserHistory.create_detailed_user_record(detailed_user_obj.detailed_user_id, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_random_password_generate(request_data, user):
        try:
            if not user.is_superuser:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UNSU_0))
                return Response(CustomError.get_full_error_json(CustomError.UNSU_0), status=status.HTTP_403_FORBIDDEN)
            # Verify that user exists for provided id
            if not UserHelper.id_user_entry_exists(request_data.get("user_id")):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)
            
            user_obj = UserHelper.get_user_obj(request_data.get("user_id"))
            # If the user access of SU and requested email is not same, return UDNE
            if user_obj.db_access != user.db_access:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)
            # Generate password
            password = UserHelper.generate_random_password()

            # Email password to user
            email_title = "Aukai Account Password Has Changed"
            email_message = "The new (temporary) password for " + str(user_obj.email) + " account is: " + str(password)
            email_response = Email.send_email_notification([user.email, user_obj.email], email_title, email_message)
            if email_response.status_code != status.HTTP_200_OK:
                return email_response

            # Update password
            UserUpdater.update_user_password(user_obj, password)

            # Create user record
            if(not UserHistory.create_user_record(user_obj.id)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_user_permission(request_data, user):
        try:
            permission = request_data.get("role_permissions")
            update_permission = UserUpdater.update_user_permission(user, permission)
            detailed_user_obj = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            if not update_permission:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UNSU_0))
                return Response(CustomError.get_full_error_json(CustomError.UNSU_0), status=status.HTTP_400_BAD_REQUEST)
            # Create detailed user record
            if(not DetailedUserHistory.create_detailed_user_record(detailed_user_obj.detailed_user_id, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_agreement(request_data, user):
        try:
            detailed_user_obj = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            if HelperMethods.validate_bool(request_data.get("agreement_accepted")) == HelperMethods.validate_bool(detailed_user_obj.agreement_accepted):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.AS_0))
                return Response(CustomError.get_full_error_json(CustomError.AS_0), status=status.HTTP_400_BAD_REQUEST)

            updated_user, updated_detailed_user, update_message = UserUpdater.update_user_account(user, detailed_user_obj, request_data, user.db_access)
            if updated_detailed_user is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UUF_0, update_message))
                return Response(CustomError.get_full_error_json(CustomError.UUF_0, update_message), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_user_config(request_data, user):
        try:
            detailed_user_obj = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            config_obj = UserHelper.get_user_config_by_user_id(detailed_user_obj.detailed_user_id, user.db_access)

            updated_config, update_message = UserUpdater.update_user_config(config_obj, request_data)
            if updated_config is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UUF_1, update_message))
                return Response(CustomError.get_full_error_json(CustomError.UUF_1, update_message), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------

    # @staticmethod
    # def handle_update_user_tablefilter(request_data, user):
    #     try:
    #         detailed_user_obj = UserHelper.get_detailed_user_obj(user.email, user.db_access)
    #         config_obj = UserHelper.get_user_config_by_user_id(detailed_user_obj.detailed_user_id, user.db_access)

    #         # Convert the table_filter string to a dictionary
    #         table_filter_dict = {}
    #         if config_obj.table_filter:
    #             table_filter_dict = ast.literal_eval(config_obj.table_filter)

    #         # Update the table_filter dictionary with the request_data
    #         table_filter_dict.update(request_data)

    #         # Convert the updated table_filter dictionary back to a string and update the UserConfiguration object
    #         updated_table_filter = str(table_filter_dict)
    #         request_data['table_filter'] = updated_table_filter

    #         updated_config, update_message = UserUpdater.update_user_config(config_obj, request_data)
    #         if updated_config is None:
    #             Logger.getLogger().error(CustomError.get_error_dev(CustomError.UUF_1, update_message))
    #             return Response(CustomError.get_full_error_json(CustomError.UUF_1, update_message), status=status.HTTP_400_BAD_REQUEST)

    #         return Response(status=status.HTTP_202_ACCEPTED)
    #     except Exception as e:
    #         Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
    #         return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def handle_update_user_tablefilter(request_data, user):
        try:
            detailed_user_obj = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            config_obj = UserHelper.get_user_config_by_user_id(detailed_user_obj.detailed_user_id, user.db_access)

            # Convert the table_filter string to a dictionary
            table_filter_dict = {}
            if config_obj.table_filter:
                table_filter_dict = ast.literal_eval(config_obj.table_filter)

            # Update the table_filter dictionary with the request_data
            for key, value in request_data.items():
                if value is None:
                    error_msg = f"Invalid value for key '{key}': {value}"
                    Logger.getLogger().error(error_msg)
                    return Response(CustomError.get_full_error_json(CustomError.UUF_1, error_msg), status=status.HTTP_400_BAD_REQUEST)
                elif isinstance(value, dict):
                    # Check for None values in sub-dictionaries
                    for sub_key, sub_value in value.items():
                        if sub_value is None:
                            error_msg = f"Invalid value for key '{sub_key}' in sub-dictionary '{key}': {sub_value}"
                            Logger.getLogger().error(error_msg)
                            return Response(CustomError.get_full_error_json(CustomError.UUF_1, error_msg), status=status.HTTP_400_BAD_REQUEST)
                table_filter_dict[key] = value

            # Convert the updated table_filter dictionary back to a string and update the UserConfiguration object
            updated_table_filter = str(table_filter_dict)
            request_data['table_filter'] = updated_table_filter

            updated_config, update_message = UserUpdater.update_user_config(config_obj, request_data)
            if updated_config is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UUF_1, update_message))
                return Response(CustomError.get_full_error_json(CustomError.UUF_1, update_message), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_delete_user_tablefilter(request_data, user):
        try:
            detailed_user_obj = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            config_obj = UserHelper.get_user_config_by_user_id(detailed_user_obj.detailed_user_id, user.db_access)

            # Convert the table_filter string to a dictionary
            table_filter_dict = {}
            if config_obj.table_filter:
                table_filter_dict = ast.literal_eval(config_obj.table_filter)

            # Update the table_filter dictionary with the request_data
            keys = list(request_data.keys())
            for key in keys:
                if request_data[key] == None or len(request_data[key]) == 0:
                    del table_filter_dict[key]
                else:
                    for subkey in request_data[key]:
                        del table_filter_dict[key][subkey]    
                    if table_filter_dict[key] == None or len(table_filter_dict[key]) == 0:
                        del table_filter_dict[key]

            # Convert the updated table_filter dictionary back to a string and update the UserConfiguration object
            updated_table_filter = str(table_filter_dict)
            request_data['table_filter'] = updated_table_filter

            updated_config, update_message = UserUpdater.update_user_config(config_obj, request_data)
            if updated_config is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UUF_1, update_message))
                return Response(CustomError.get_full_error_json(CustomError.UUF_1, update_message), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
