from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_request import AssetRequestModel
from api.Models.asset_request_history import AssetRequestModelHistory
from api.Models.RolePermissions import RolePermissions
from ..UserManager.UserHelper import UserHelper
from ..AssetManager.AssetHelper import AssetHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetRequestHelper():
    
    @staticmethod
    def select_related_to_asset_request(queryset):
        return queryset.select_related('created_by', 'modified_by', 'location', 'business_unit', 'equipment', 'equipment__asset_type', 'justification', 'equipment__manufacturer', 'disposal')

    # This method will take a asset request qs and filter it to only show asset requests relevant to user
    @staticmethod
    def filter_asset_requests_for_user(asset_request_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return asset_request_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return asset_request_qs.filter(business_unit__location__in=user_locations)

    @staticmethod
    def get_in_progress_asset_requests(db_name):
        return AssetRequestModel.objects.using(db_name).filter(status__in=AssetRequestModel.incomplete_status_values)

    @staticmethod
    def get_delivered_asset_requests(db_name):
        return AssetRequestModel.objects.using(db_name).filter(status__in=AssetRequestModel.complete_status_values)

    @staticmethod
    def get_asset_request_by_id(_id, db_name):
        try:
            return AssetRequestModel.objects.using(db_name).get(id=_id), Response(status=status.HTTP_302_FOUND)
        except AssetRequestModel.DoesNotExist as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ARDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ARDNE_0, e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_asset_request_by_custom_id(custom_id, db_name):
        try:
            return AssetRequestModel.objects.using(db_name).get(custom_id=custom_id), Response(status=status.HTTP_302_FOUND)
        except AssetRequestModel.DoesNotExist as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ARDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ARDNE_0, e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def asset_request_exists_by_id(asset_request_id, db_name):
        return AssetRequestModel.objects.using(db_name).filter(id=asset_request_id).exists()

    @staticmethod
    def get_all_non_null_ids(db_name):
        return set(AssetRequestModel.objects.using(db_name).exclude(disposal__isnull=True).values_list('disposal',flat=True))

    @staticmethod
    def get_asset_requests_for_daterange(start_date, end_date, db_name):
        return AssetRequestModel.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_asset_requests_history_for_daterange(start_date, end_date, db_name):
        return AssetRequestModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def is_status_valid(status):
        if status in dict(AssetRequestModel.asset_request_status_choices):
            return True
        return False