from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_daily_checks import AssetDailyChecksModel
from api.Models.asset_daily_checks_history import AssetDailyChecksModelHistory
from api.Models.asset_daily_checks_comment import AssetDailyChecksComment
from ..AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from api.Models.DetailedUser import DetailedUser
from api.Models.RolePermissions import RolePermissions
from api.Models.asset_model import AssetModel
from ..UserManager.UserHelper import UserHelper
from ..AssetManager.AssetHelper import AssetHelper
from core.Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DailyOperationalCheckHelper():

    @staticmethod
    def select_related_to_daily_check(qs):
        return qs.select_related('created_by', 'modified_by', 'location', 'VIN__equipment_type__asset_type')

    @staticmethod
    def get_daily_check_ser_context(daily_check_id_list, user):
        comments = DailyOperationalCheckHelper.get_daily_check_comments_for_daily_checks_list(daily_check_id_list, user.db_access)
        return {
            'users': UserHelper.get_all_users_for_company(user.db_access).values(),
            'comments': comments
            }

    # This method will take a daily checks qs and filter it to only show daily checks relevant to user
    @staticmethod
    def filter_daily_operational_checks_for_user(daily_checks_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return daily_checks_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return daily_checks_qs.filter(location__in=user_locations)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_daily_operators_check_by_id(op_check_id, db_name):
        try:
            return AssetDailyChecksModel.objects.using(db_name).get(daily_check_id=op_check_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.OCDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.OCDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_daily_operators_check_by_custom_id(custom_op_check_id, db_name):
        try:
            return AssetDailyChecksModel.objects.using(db_name).get(custom_id=custom_op_check_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.OCDNE_1, e))
            return None, Response(CustomError.get_full_error_json(CustomError.OCDNE_1, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_operational_checks_by_vin(vin, db_name):
        try:
            return AssetDailyChecksModel.objects.using(db_name).filter(VIN__VIN=vin), Response(status=status.HTTP_302_FOUND)
        except AssetDailyChecksModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.OCDNE_2))
            return Response(CustomError.get_full_error_json(CustomError.OCDNE_2), status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_daily_check_comments(db_name):
        return AssetDailyChecksComment.objects.using(db_name).all()

    @staticmethod
    def get_daily_check_comments_for_daterange(start_date, end_date, db_name):
        return AssetDailyChecksComment.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_daily_check_comments_for_daily_checks_list(daily_checks_id_list, db_name):
        return AssetDailyChecksComment.objects.using(db_name).filter(daily_check__in=daily_checks_id_list)

    @staticmethod
    def get_daily_checks_for_daterange(start_date, end_date, db_name):
        return AssetDailyChecksModel.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_daily_checks_history_for_daterange(start_date, end_date, db_name):
        return AssetDailyChecksModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_daily_check_location(daily_check_obj):
        if daily_check_obj.location != None:
            return daily_check_obj.location
        else: # If None return 0 as there are no location IDs that are 0
            return 0

    # -----------------------------------------------------------------------

    @staticmethod
    def check_request_info_present(request_data, db_name):
        try:
            asset_obj = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), db_name)
            hours_or_mileage = asset_obj.hours_or_mileage.lower()

            if hours_or_mileage == AssetModel.Mileage.lower():
                if len(str(request_data.get("mileage"))) == 0 or request_data.get("mileage") is None or str(request_data.get("mileage")) == "-1":
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.DOCI_0))
                    return Response(CustomError.get_full_error_json(CustomError.DOCI_0), status=status.HTTP_400_BAD_REQUEST)
            if hours_or_mileage == AssetModel.Hours.lower():
                if len(str(request_data.get("hours"))) == 0 or request_data.get("hours") is None or str(request_data.get("hours")) == "-1":
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.DOCI_1))
                    return Response(CustomError.get_full_error_json(CustomError.DOCI_1), status=status.HTTP_400_BAD_REQUEST)
            if hours_or_mileage == AssetModel.Both.lower():
                if (len(str(request_data.get("mileage"))) == 0 or request_data.get("mileage") is None or str(request_data.get("mileage")) == "-1") or (len(str(request_data.get("hours"))) == 0 or request_data.get("hours") is None or str(request_data.get("hours")) == "-1"):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.DOCI_2))
                    return Response(CustomError.get_full_error_json(CustomError.DOCI_2), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def generate_op_check_metrics_string(op_check_obj, db_name):
        asset = AssetHelper.get_asset_by_VIN(op_check_obj.VIN, db_name)
        hours_or_mileage = asset.hours_or_mileage.lower()
        if hours_or_mileage == AssetModel.Mileage.lower():
            return "Asset mileage was set to " + str(op_check_obj.mileage) + "."
        if hours_or_mileage == AssetModel.Hours.lower():
            return "Asset hours were set to " + str(op_check_obj.hours) + "."
        if hours_or_mileage == AssetModel.Both.lower():
            return "Asset mileage was set to " + str(op_check_obj.mileage) + " and asset hours were set to " + str(op_check_obj.hours) + "."
        if hours_or_mileage == AssetModel.Neither.lower():
            return "This asset does not track usage so hours/mileage were not updated."
        return ""


    # Checks if the string provided fits one of the check field names in the daily checks model
    @staticmethod
    def check_if_check_is_valid(comments):
        all_fields = AssetDailyChecksModel._meta.fields
        clean_field_names = [str(h).split('.')[2] for h in all_fields]

        for comment in comments:
            
            if comment.get("check") not in clean_field_names:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.DOCI_3))
                return Response(CustomError.get_full_error_json(CustomError.DOCI_3), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_checks_from_request_data(request_data):
        fields = []
        for field in request_data:
            value = request_data.get(field)
            if (isinstance(value, bool) or isinstance(value, str)) and field != "operable" and field != "is_tagout":
                if isinstance(HelperMethods.validate_bool(value), bool):
                    fields.append(field)
        return fields

    @staticmethod
    #returns True if there are issues with the operational check, and False if there are none
    def check_operational_check_issues(request_data):
        for field in DailyOperationalCheckHelper.get_checks_from_request_data(request_data):
            value = HelperMethods.validate_bool(request_data.get(field))
            if value == False:
                return True
        return False


    @staticmethod
    def update_daily_op_check_dict(request_data, db_name):
        request_data["location"] = AssetHelper.get_asset_location_id(request_data.get("VIN"), db_name)
        return request_data