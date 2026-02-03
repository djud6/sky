from rest_framework.response import Response
from rest_framework import status
from api.Models.notification_configuration import NotificationConfiguration
from .NotificationHelper import NotificationHelper
from core.Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)
    
class NotificationUpdater():
    

    @staticmethod
    def update_notification_config_fields(config_entry, request_data, detailed_user):
        try:
            if not len(str(request_data.get("active"))) == 0 and request_data.get("active") is not None:
                config_entry.active = HelperMethods.validate_bool(request_data.get("active"))
            if not len(str(request_data.get("fields"))) == 0 and request_data.get("fields") is not None:
                config_entry.fields = request_data.get("fields")
            if not len(str(request_data.get("triggers"))) == 0 and request_data.get("triggers") is not None:
                config_entry.triggers = request_data.get("triggers")
            if not len(str(request_data.get("custom_text"))) == 0 and request_data.get("custom_text") is not None:
                config_entry.custom_text = request_data.get("custom_text")
            if not len(str(request_data.get("recipient_type"))) == 0 and request_data.get("recipient_type") is not None:
                if NotificationHelper.is_recipient_type_valid(str(request_data.get("recipient_type"))):
                    config_entry.recipient_type = request_data.get("recipient_type")
            if not len(str(request_data.get("users"))) == 0 and request_data.get("users") is not None:
                config_entry.users = request_data.get("users")
            if not len(str(request_data.get("locations"))) == 0 and request_data.get("locations") is not None:
                config_entry.locations = request_data.get("locations")
            if not len(str(request_data.get("business_units"))) == 0 and request_data.get("business_units") is not None:
                config_entry.business_units = request_data.get("business_units")
            if not len(str(request_data.get("roles"))) == 0 and request_data.get("roles") is not None:
                config_entry.roles = request_data.get("roles")

            config_entry.modified_by = detailed_user

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.TUF_15, e)
            return Response(CustomError.get_full_error_json(CustomError.TUF_15, e), status=status.HTTP_400_BAD_REQUEST)
        
    @staticmethod
    def bulk_update_all_fields(queryset, db_name):
        try:
            fields = ['active', 'fields', 'triggers', 'custom_text', 'recipient_type',
                      'users', 'locations', 'roles', 'business_units', 'date_modified', 'modified_by']
            NotificationConfiguration.objects.using(db_name).bulk_update(queryset, fields)
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
