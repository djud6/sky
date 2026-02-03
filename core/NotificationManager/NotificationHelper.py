from rest_framework.response import Response
from rest_framework import status
from api.Models.notification_configuration import NotificationConfiguration
from core.UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)
    
class NotificationHelper():
    
    @staticmethod
    def get_all_notification_configs(db_name):
        return NotificationConfiguration.objects.using(db_name).all()
    
    @staticmethod
    def get_notification_configs_by_ids(ids, db_name):
        return NotificationConfiguration.objects.using(db_name).filter(id__in=ids)
    
    @staticmethod
    def get_notification_config_by_name(name, db_name):
        try:
            return NotificationConfiguration.objects.using(db_name).get(name=name), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.NCDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.NCDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def is_recipient_type_valid(recipient_type):
        if recipient_type in dict(NotificationConfiguration.recipient_type_choices):
            return True
        return False
    
    @staticmethod
    def parse_fields_to_list(fields):
        return fields.split("-")[1:-1]
    
    @staticmethod
    def parse_triggers_to_list(triggers):
        return triggers.split("-")[1:-1]
    
    @staticmethod
    def parse_users_to_list(users):
        return users.split("-")[1:-1]

    @staticmethod
    def parse_locations_to_list(locations):
        return locations.split("-")[1:-1]
    
    @staticmethod
    def parse_business_units_to_list(business_units):
        return business_units.split("-")[1:-1]
    
    @staticmethod
    def parse_roles_to_list(roles):
        return roles.split("-")[1:-1]
    
    @staticmethod
    def get_recipients_for_notification(notification_config, db_name):
        '''
        Will return the emails of recipients for the type 
        of recipient mode indicated by recipient_type. 
        '''

        if notification_config.recipient_type == NotificationConfiguration.user:
            if notification_config.users is None:
                return []
            user_ids = NotificationHelper.parse_users_to_list(notification_config.users)
            return list(UserHelper.get_detailed_users_by_ids(user_ids, db_name).values_list('email', flat=True))
        elif notification_config.recipient_type == NotificationConfiguration.location:
            if notification_config.locations is None:
                return []
            location_ids = NotificationHelper.parse_locations_to_list(notification_config.locations)
            return list(set(UserHelper.get_detailed_users_by_location_ids(location_ids, db_name).values_list('email', flat=True)))
        elif notification_config.recipient_type == NotificationConfiguration.business_unit:
            if notification_config.business_units is None:
                return []
            business_unit_ids = NotificationHelper.parse_business_units_to_list(notification_config.business_units)
            return list(UserHelper.get_detailed_users_by_business_unit_ids(business_unit_ids, db_name).values_list('email', flat=True))
        elif notification_config.recipient_type == NotificationConfiguration.role:
            if notification_config.roles is None:
                return []
            role_ids = NotificationHelper.parse_roles_to_list(notification_config.roles)
            return list(UserHelper.get_detailed_users_by_role_ids(role_ids, db_name).values_list('email', flat=True))
        else:
            print("No matching recipient type...")
            return []