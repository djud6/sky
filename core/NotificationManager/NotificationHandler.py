from rest_framework.response import Response
from rest_framework import status
from api.Serializers.serializers import NotificationConfigurationSerializer
from .NotificationHelper import NotificationHelper
from .NotificationUpdater import NotificationUpdater
from core.UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)
    
class NotificationHandler():
    
    @staticmethod
    def handle_list_notification_configs(user):
        try:
            queryset = NotificationHelper.get_all_notification_configs(user.db_access)
            ser = NotificationConfigurationSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        

    @staticmethod
    def handle_edit_notification_configs(request_data, user):
        try:
            queryset = NotificationHelper.get_notification_configs_by_ids(request_data.keys(), user.db_access)
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            for entry in queryset:
                update_data = request_data.get(str(entry.id))
                resp = NotificationUpdater.update_notification_config_fields(entry, update_data, detailed_user)
                if resp.status_code != status.HTTP_202_ACCEPTED:
                    return resp
            
            resp = NotificationUpdater.bulk_update_all_fields(queryset, user.db_access)
            if resp.status_code != status.HTTP_202_ACCEPTED:
                return resp

            ser = NotificationConfigurationSerializer(queryset, many=True)
            
            return Response(ser.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        