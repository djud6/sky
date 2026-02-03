from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_issue import AssetIssueModel
from api.Models.asset_issue_history import AssetIssueModelHistory
from api.Models.RolePermissions import RolePermissions
from api.Models.asset_issue_file import AssetIssueFileModel
from api.Models.accident_report import AccidentModel
from api.Models.asset_issue_category import AssetIssueCategory
from ..UserManager.UserHelper import UserHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..Helper import HelperMethods
from django.core.exceptions import ObjectDoesNotExist
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.db.models import Q
from datetime import datetime
from datetime import timezone
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class IssueHelper():

    @staticmethod
    def select_related_to_issue(queryset):
        return queryset.select_related('accident_id','repair_id', 'created_by', 'modified_by', 'location', 'VIN__current_location', 'VIN__original_location', 'VIN', 'VIN__equipment_type__asset_type')

    # -----------------------------------------------------------------------

    @staticmethod
    def get_issue_ser_context(issue_id_list, db_name):
        # Get issue files and secure urls
        container_name = "issues"
        issue_files = AssetIssueFileModel.objects.using(db_name).filter(issue__in=issue_id_list).order_by('-file_id').values()
        for issue_file in issue_files:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, container_name, issue_file.get('file_url'))
            issue_file['file_url'] = secure_file_url
        return {
            'all_issue_files': issue_files
            }

    # This method will take an issue qs and filter it to only show issues relevant to user
    @staticmethod
    def filter_issues_for_user(issue_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return issue_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return issue_qs.filter(location__in=user_locations)

    @staticmethod
    def get_all_issues(db_name):
        return AssetIssueModel.objects.using(db_name).select_related('location', 'accident_id', 'repair_id').all()

    @staticmethod
    def get_all_issues_in_last_x_days(days, db_name):
        start_date = HelperMethods.subtract_time_from_datetime(datetime.utcnow(), days, time_unit="days").replace(tzinfo=timezone.utc)
        return AssetIssueModel.objects.using(db_name).filter(issue_created__gte=start_date)

    @staticmethod
    def get_issues_by_accident_id(accident_id, db_name):
        return AssetIssueModel.objects.using(db_name).filter(accident_id=accident_id)

    @staticmethod
    def get_issue_by_repair_id(repair_id, db_name):
        return AssetIssueModel.objects.using(db_name).filter(repair_id=repair_id)

    @staticmethod
    def get_issues_for_repair_list(repair_id_list, db_name):
        return AssetIssueModel.objects.using(db_name).filter(repair_id__in=repair_id_list)

    @staticmethod
    def get_issue_exists(issue_id, db_name):
        return AssetIssueModel.objects.using(db_name).filter(issue_id=issue_id).exists()

    @staticmethod
    def get_issues(vin, db_name):
        try:
            asset_issues = AssetIssueModel.objects.using(db_name).filter(VIN__VIN=vin)
            return asset_issues, Response(status=status.HTTP_200_OK)
        except AssetIssueModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IDNE_1))
            return None, Response(CustomError.get_full_error_json(CustomError.IDNE_1), status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_issue_by_id(issue_id, db_name):
        try:
            asset_issues = AssetIssueModel.objects.using(db_name).get(issue_id=issue_id)
            return asset_issues, Response(status=status.HTTP_302_FOUND)
        except AssetIssueModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IDNE_0))
            return None, Response(CustomError.get_full_error_json(CustomError.IDNE_0), status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_issue_by_custom_id(custom_issue_id, db_name):
        try:
            asset_issues = AssetIssueModel.objects.using(db_name).get(custom_id=custom_issue_id)
            return asset_issues, Response(status=status.HTTP_302_FOUND)
        except AssetIssueModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IDNE_3))
            return None, Response(CustomError.get_full_error_json(CustomError.IDNE_3), status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_issue_category_by_id(category_id, db_name):
        try:
            asset_issues = AssetIssueCategory.objects.using(db_name).get(id=category_id)
            return asset_issues, Response(status=status.HTTP_302_FOUND)
        except AssetIssueModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IDNE_2))
            return None, Response(CustomError.get_full_error_json(CustomError.IDNE_2), status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_issue_file_entries_for_daterange(start_date, end_date, db_name):
        return AssetIssueFileModel.objects.using(db_name).filter(file_created__range=[start_date, end_date])

    @staticmethod
    def get_issues_for_daterange(start_date, end_date, db_name):
        return AssetIssueModel.objects.using(db_name).filter(issue_created__range=[start_date, end_date])

    @staticmethod
    def get_issue_history_for_daterange(start_date, end_date, db_name):
        return AssetIssueModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_issue_location(issue_obj):
        if issue_obj.location != None:
            return issue_obj.location
        else: # If None return 0 as there are no location IDs that are 0
            return 0

    # -----------------------------------------------------------------------

    @staticmethod
    def is_result_of_accident(issue_obj):
        if(issue_obj.accident_id is not None):
            return True
        return False

    # -----------------------------------------------------------------------
    
    @staticmethod
    def update_issue_dict(request_data, db_name):
        request_data["location"] = AssetHelper.get_asset_location_id(request_data.get("VIN"), db_name)
        return request_data