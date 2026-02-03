from core.Helper import HelperMethods
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from api.Models.maintenance_request_file import MaintenanceRequestFile
from api.Models.maintenance_request import MaintenanceRequestModel
from rest_framework.response import Response
from rest_framework import status
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.maintenance_request_history import MaintenanceRequestModelHistory
from api.Models.RolePermissions import RolePermissions
from api.Models.asset_model import AssetModel
from ..AssetManager.AssetHelper import AssetHelper
from ..UserManager.UserHelper import UserHelper
from api.Models.DetailedUser import DetailedUser
from ..Helper import HelperMethods
from django.db.models import Q
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

        
class MaintenanceHelper():

    @staticmethod
    def select_related_to_maintenance(queryset):
        return queryset.select_related('created_by', 'modified_by', 'location', 'VIN__current_location', 'VIN__original_location', 'assigned_vendor', 'inspection_type', 'VIN__equipment_type__asset_type', 'VIN__equipment_type__manufacturer')

    @staticmethod
    def select_related_to_maintenance_rule(queryset):
        return queryset.select_related('created_by', 'modified_by', 'inspection_type', 'VIN__current_location', 'VIN__original_location')

    # This method will take a accidents qs and filter it to only show accidents relevant to user
    @staticmethod
    def filter_maintenance_for_user(maintenance_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return maintenance_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return maintenance_qs.filter(location__in=user_locations)

    @staticmethod
    def filter_maintenance_rules_for_user(maintenance_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return maintenance_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return maintenance_qs.filter(location__in=user_locations)

    # -------------------------------------------------------------------------------------

    @staticmethod
    def get_all_maintenance(db_name):
        return MaintenanceRequestModel.objects.using(db_name).select_related('location').all()

    @staticmethod
    def get_maintenance_by_ids(maintenance_ids, db_name):
        return MaintenanceRequestModel.objects.using(db_name).filter(maintenance_id__in=maintenance_ids)
        
    @staticmethod
    def get_work_order(_id, company_name):
        identifier = "-m-"
        return str(company_name) + identifier + str(_id)

    @staticmethod
    def get_maintenance_ser_context(maintenance_id_list, db_name):
        # Get maintenance files and secure urls
        container_name = "maintenance"
        maintenance_files = MaintenanceRequestFile.objects.using(db_name).filter(maintenance_request__in=maintenance_id_list).order_by('-file_id').values()
        for maintenance_file in maintenance_files:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, container_name, maintenance_file.get('file_url'))
            maintenance_file['file_url'] = secure_file_url
        return {
            'maintenance_files': maintenance_files
            }

    # Get VINs that are in daterange provided and are Active
    @staticmethod
    def get_maintenance_for_inop_in_daterange(datetime_start, datetime_end, db_name):
        return MaintenanceRequestModel.objects.using(db_name).filter(VIN__status=AssetModel.Active, 
        available_pickup_date__range=[datetime_start, datetime_end])

    # Get repairs that are in daterange and vinlist provided
    @staticmethod
    def get_maintenance_in_vinlist_and_daterange(datetime_start, datetime_end, vin_list, db_name):
        return MaintenanceRequestModel.objects.using(db_name).filter(VIN__in=vin_list, 
        available_pickup_date__range=[datetime_start, datetime_end])

    @staticmethod
    def get_maintenance_request_by_id(maintenance_id, db_name):
        try:
            return MaintenanceRequestModel.objects.using(db_name).get(maintenance_id=maintenance_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MRDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.MRDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_maintenance_request_by_work_order(work_order_id, db_name):
        try:
            return MaintenanceRequestModel.objects.using(db_name).get(work_order=work_order_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MRDNE_1, e))
            return None, Response(CustomError.get_full_error_json(CustomError.MRDNE_1, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_maintenance_exists_by_id(maintenance_id, db_name):
        return MaintenanceRequestModel.objects.using(db_name).filter(maintenance_id=maintenance_id).exists()
    
    @staticmethod
    def does_maintenance_entry_exist_by_other(maintenance_row, db_name):
        """
        Finds if a maintenance entry already exists based on fields other than the ID field.
        """
        return MaintenanceRequestModel.objects.using(db_name).filter(VIN=maintenance_row.get("VIN"),
            inspection_type__inspection_code=maintenance_row.get("inspection_code"),
            location__location_name=maintenance_row.get("location_name"),
            date_completed=HelperMethods.date_string_to_datetime(HelperMethods.ParseDateToDateField(maintenance_row.get("date_completed")))).exists()

    @staticmethod
    def get_maintenance_after_date_by_status_and_location(complete_status, date, location_id, db_name):
        if(complete_status):
            return MaintenanceRequestModel.objects.using(db_name).filter(date_created__gte=date, status = MaintenanceRequestModel.complete, location=location_id)

    @staticmethod
    def get_maintenance_after_date(date, db_name):
        return MaintenanceRequestModel.objects.using(db_name).filter(date_created__gte=date)

    @staticmethod
    def get_maintenance_for_daterange(start_date, end_date, db_name):
        return MaintenanceRequestModel.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_maintenance_file_entries_for_daterange(start_date, end_date, db_name):
        return MaintenanceRequestFile.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_maintenance_history_for_daterange(start_date, end_date, db_name):
        return MaintenanceRequestModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_maintenance_location(maintenance_obj):
        if maintenance_obj.location != None:
            return maintenance_obj.location
        else: # If None return 0 as there are no location IDs that are 0
            return 0

    @staticmethod
    #Checks the cycle asset tracks and compares with requested rule
    def check_maintenance_cycle_inputs(request_data, db_name):

        asset_obj = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), db_name)
        hours_or_mileage = asset_obj.hours_or_mileage.lower()

        if hours_or_mileage == 'both':
            return Response(status=status.HTTP_200_OK)

        elif hours_or_mileage == 'neither' and (request_data.get("hour_cycle") or request_data.get("mileage_cycle")) is not None:
            Logger.getLogger().error(CustomError.MRVTC_0)
            return Response(CustomError.get_full_error_json(CustomError.MRVTC_0), status=status.HTTP_400_BAD_REQUEST)

        elif hours_or_mileage == 'hours' and request_data.get("mileage_cycle") is not None:
            Logger.getLogger().error(CustomError.MRVTC_1)
            return Response(CustomError.get_full_error_json(CustomError.MRVTC_1), status=status.HTTP_400_BAD_REQUEST)

        elif hours_or_mileage == 'mileage' and request_data.get("hour_cycle") is not None:
            Logger.getLogger().error(CustomError.MRVTC_2)
            return Response(CustomError.get_full_error_json(CustomError.MRVTC_2), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_200_OK)

    @staticmethod
    #Checks to see if the value is greater than 0
    def validate_maintenance_cycle_inputs(request_data):
        
        if not len(str(request_data.get("hour_cycle"))) == 0 and request_data.get("hour_cycle") is not None:
            if request_data.get("hour_cycle") < 0:
                Logger.getLogger().error(CustomError.MRVLU_0)
                return Response(CustomError.get_full_error_json(CustomError.MRVLU_0), status=status.HTTP_400_BAD_REQUEST)

        if not len(str(request_data.get("mileage_cycle"))) == 0 and request_data.get("mileage_cycle") is not None:
            if request_data.get("mileage_cycle") < 0:
                Logger.getLogger().error(CustomError.MRVLU_0)
                return Response(CustomError.get_full_error_json(CustomError.MRVLU_0), status=status.HTTP_400_BAD_REQUEST)

        if not len(str(request_data.get("time_cycle"))) == 0 and request_data.get("time_cycle") is not None:
            if request_data.get("time_cycle") < 0:
                Logger.getLogger().error(CustomError.MRVLU_0)
                return Response(CustomError.get_full_error_json(CustomError.MRVLU_0), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def check_request_info_present(request_data, db_name):
        try:
            requested_data = request_data.get('assets')
            for maint_req_data in requested_data:
                asset_obj = AssetHelper.get_asset_by_VIN(maint_req_data.get("VIN"), db_name)
                if not AssetHelper.check_asset_status_active(maint_req_data.get("VIN"), db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                hours_or_mileage = asset_obj.hours_or_mileage.lower()

                if hours_or_mileage == AssetModel.Mileage.lower():
                    if len(str(maint_req_data.get("mileage"))) == 0 or maint_req_data.get("mileage") is None or str(maint_req_data.get("mileage")) == "-1":
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.MRI_0))
                        return Response(CustomError.get_full_error_json(CustomError.MRI_0), status=status.HTTP_400_BAD_REQUEST)

                if hours_or_mileage == AssetModel.Hours.lower():
                    if len(str(maint_req_data.get("hours"))) == 0 or maint_req_data.get("hours") is None or str(maint_req_data.get("hours")) == "-1":
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.MRI_1))
                        return Response(CustomError.get_full_error_json(CustomError.MRI_1), status=status.HTTP_400_BAD_REQUEST)

                if hours_or_mileage == AssetModel.Both.lower():
                    if (len(str(maint_req_data.get("mileage"))) == 0 or maint_req_data.get("mileage") is None or str(maint_req_data.get("mileage")) == "-1") or (len(str(maint_req_data.get("hours"))) == 0 or maint_req_data.get("hours") is None or str(maint_req_data.get("hours")) == "-1"):
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.MRI_2))
                        return Response(CustomError.get_full_error_json(CustomError.MRI_2), status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def check_location_info(requested_data, db_name):
        try:
            if len(requested_data) > 1:
                locations = []
                for maint_req in requested_data:
                    locations.append(maint_req.get('location'))
                locations_len = len(HelperMethods.get_unique_values_from_list(locations))
                if locations_len > 1:                
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def revert_status(maintenance_id, db_name):
        try:
            previous_status = MaintenanceRequestModelHistory.objects.using(db_name).filter(maintenance__maintenance_id = maintenance_id).exclude(status=MaintenanceRequestModel.complete).order_by('date').first()
            if(previous_status.status == "NA"):
                return MaintenanceRequestModel.awaiting_approval
            return previous_status.status
        except Exception as e: 
            return MaintenanceRequestModel.awaiting_approval


    @staticmethod
    def update_batch_maintenance_dict(request_data, db_name):
        updated_request_data = []
        location = AssetHelper.get_asset_location_id(request_data[0].get("VIN"), db_name)
        for maintenance in request_data:
            maintenance["location"] = location
            updated_request_data.append(maintenance)
        return updated_request_data

    @staticmethod
    def update_maintenance_dict(request_data, db_name):
        request_data["location"] = AssetHelper.get_asset_location_id(request_data.get("VIN"), db_name)
        return request_data
        
    @staticmethod
    def validate_purpose(purpose):
        if purpose in dict(MaintenanceRequestFile.file_purpose_choices):
            return True
        return False

    @staticmethod
    def is_status_valid(status):
        if status in dict(MaintenanceRequestModel.maintenance_status_choices):
            return True
        return False
