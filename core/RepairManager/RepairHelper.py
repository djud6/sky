from rest_framework.response import Response
from rest_framework import status
from api.Models.repairs import RepairsModel
from api.Models.repairs_history import RepairsModelHistory
from api.Models.repair_file import RepairFile
from api.Models.asset_model import AssetModel
from ..UserManager.UserHelper import UserHelper
from api.Models.RolePermissions import RolePermissions
from ..IssueManager.IssueHelper import IssueHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..CostManager.CostHelper import PartsHelper, LaborHelper
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.db.models import Q
from api.Models.repairs_history import RepairsModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RepairHelper():

    @staticmethod
    def select_related_to_repair(queryset):
        return queryset.select_related('created_by', 'modified_by', 'VIN', 'location', 'VIN__current_location', 'VIN__original_location', 'vendor', 'VIN__equipment_type__asset_type', 'VIN__equipment_type__manufacturer', 'VIN__equipment_type', 'VIN__department')

    # TODO: Currently adding the issue_files context into the serializer slows down the serializer alot. 
    # May need to only pull issue files and specifically needed.
    @staticmethod
    def get_repair_ser_context(repair_id_list, db_name):
        # Get repair files and secure urls
        container_name = "repair"
        repair_files = RepairFile.objects.using(db_name).filter(repair_id__in=repair_id_list).order_by('-file_id').values()
        for repair_file in repair_files:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, container_name, repair_file.get('file_url'))
            repair_file['file_url'] = secure_file_url
        # Get issues for repair
        issues = IssueHelper.select_related_to_issue(IssueHelper.get_issues_for_repair_list(repair_id_list, db_name))
        return {
            'all_issues': issues,
            'all_repair_files': repair_files
            }

    # This method will take a repair qs and filter it to only show repairs relevant to user
    @staticmethod
    def filter_repairs_for_user(repair_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return repair_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return repair_qs.filter(location__in=user_locations)

    # -------------------------------------------------------------------------------------

    @staticmethod
    def get_all_repairs(db_name):
        return RepairsModel.objects.using(db_name).select_related('location').all()

    @staticmethod
    def get_repairs_by_ids(repair_ids, db_name):
        return RepairsModel.objects.using(db_name).filter(repair_id__in=repair_ids)

    # Get repairs that are in daterange provided and their asset has status == Active
    @staticmethod
    def get_repairs_for_inop_in_daterange(datetime_start, datetime_end, db_name):
        return RepairsModel.objects.using(db_name).filter(VIN__status=AssetModel.Active, 
        available_pickup_date__range=[datetime_start, datetime_end])

    # Get repairs that are in daterange and vinlist provided
    @staticmethod
    def get_repairs_in_vinlist_and_daterange(datetime_start, datetime_end, vin_list, db_name):
        return RepairsModel.objects.using(db_name).filter(VIN__in=vin_list, 
        available_pickup_date__range=[datetime_start, datetime_end])

    @staticmethod
    def get_repairs_for_vin(vin, db_name):
        return RepairsModel.objects.using(db_name).filter(VIN=vin)

    @staticmethod
    def get_repair_request_by_id(repair_id, db_name):
        try:
            return RepairsModel.objects.using(db_name).get(repair_id=repair_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.RDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_repair_request_by_work_order(work_order_id, db_name):
        try:
            return RepairsModel.objects.using(db_name).get(work_order=work_order_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RDNE_1, e))
            return None, Response(CustomError.get_full_error_json(CustomError.RDNE_1, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_repair_request_by_disposal_id(disposal_id, db_name):
        try:
            return RepairsModel.objects.using(db_name).get(disposal=disposal_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RDNE_2, e))
            return None, Response(CustomError.get_full_error_json(CustomError.RDNE_2, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_repairs_by_accident_id(accident_id, db_name):
        issues = IssueHelper.get_issues_by_accident_id(accident_id, db_name)
        repair_ids = issues.values_list('repair_id', flat=True)
        return RepairsModel.objects.using(db_name).filter(repair_id__in=repair_ids)

    @staticmethod
    def get_repairs_after_date_by_status_and_location(complete_status, date, location_id, db_name):
        if(complete_status):
            return RepairsModel.objects.using(db_name).filter(date_created__gte=date, status =RepairsModel.complete , location=location_id)
        else :
            return RepairsModel.objects.using(db_name).filter(date_created__gte=date, location=location_id).exclude(status = RepairsModel.complete)

    @staticmethod
    def get_repairs_after_date(date, db_name):
        return RepairsModel.objects.using(db_name).filter(date_created__gte=date)

    @staticmethod
    def get_repairs_for_daterange(start_date, end_date, db_name):
        return RepairsModel.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_repair_file_entries_for_daterange(start_date, end_date, db_name):
        return RepairFile.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_repair_history_for_daterange(start_date, end_date, db_name):
        return RepairsModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_repair_location(repair_obj):
        if repair_obj.location != None:
            return repair_obj.location
        else: # If None return 0 as there are no location IDs that are 0
            return 0

    @staticmethod
    def get_all_refurbishment_work_orders(db_name):
        return RepairsModel.objects.using(db_name).filter(is_refurbishment = True)
    # -------------------------------------------------------------------------------------

    @staticmethod
    def check_request_info_present(request_data, db_name):
        try:
            requested_data = request_data.get('repair_data')
            asset_obj = AssetHelper.get_asset_by_VIN(requested_data.get("VIN"), db_name)
            hours_or_mileage = asset_obj.hours_or_mileage.lower()

            if hours_or_mileage == AssetModel.Mileage.lower():
                if len(str(requested_data.get("mileage"))) == 0 or requested_data.get("mileage") is None or str(requested_data.get("mileage")) == "-1":
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.RRI_0))
                    return Response(CustomError.get_full_error_json(CustomError.RRI_0), status=status.HTTP_400_BAD_REQUEST)
            if hours_or_mileage == AssetModel.Hours.lower():
                if len(str(requested_data.get("hours"))) == 0 or requested_data.get("hours") is None or str(requested_data.get("hours")) == "-1":
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.RRI_1))
                    return Response(CustomError.get_full_error_json(CustomError.RRI_1), status=status.HTTP_400_BAD_REQUEST)
            if hours_or_mileage == AssetModel.Both.lower():
                if (len(str(requested_data.get("mileage"))) == 0 or requested_data.get("mileage") is None or str(requested_data.get("mileage")) == "-1") or (len(str(requested_data.get("hours"))) == 0 or requested_data.get("hours") is None or str(requested_data.get("hours")) == "-1"):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.RRI_2))
                    return Response(CustomError.get_full_error_json(CustomError.RRI_2), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def revert_status(repair_id, db_name):
        try:
            previous_status = RepairsModelHistory.objects.using(db_name).filter(repair__repair_id = repair_id).exclude(status=RepairsModel.complete).order_by('date').first()
            if(previous_status.status == "NA"):
                return RepairsModel.awaiting_approval
            return previous_status.status
        except Exception as e: 
            return RepairsModel.awaiting_approval
            
    # -------------------------------------------------------------------------------------

    @staticmethod
    def repair_has_cost(repair_id, db_name):
        issues_ids = list(IssueHelper.get_issue_by_repair_id(repair_id, db_name).values_list('issue_id', flat=True))
        part_costs_exist = PartsHelper.get_parts_by_issue_list(issues_ids, db_name).exists()
        labor_costs_exist = LaborHelper.get_labor_cost_by_issue_id_list(issues_ids, db_name).exists()
        if part_costs_exist or labor_costs_exist:
            return True
        return False

    # -------------------------------------------------------------------------------------
    
    @staticmethod
    def repair_exists_by_id(repair_id, db_name):
        return RepairsModel.objects.using(db_name).filter(repair_id=repair_id).exists()

    # -------------------------------------------------------------------------------------

    @staticmethod
    def update_repair_dict(request_data, db_name):
        request_data["location"] = AssetHelper.get_asset_location_id(request_data.get("VIN"), db_name)
        return request_data

    @staticmethod
    def validate_purpose(file_purpose):
        if file_purpose in dict(RepairFile.file_purpose_choices):
            return True
        return False

    @staticmethod
    def is_status_valid(status):
        if status in dict(RepairsModel.repair_status_choices):
            return True
        return False