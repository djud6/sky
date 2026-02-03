from core.AssetManager.AssetHelper import AssetHelper
from api.Models.maintenance_forecast import MaintenanceForecastRules
from rest_framework.response import Response
from rest_framework import status
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.maintenance_request_file import MaintenanceRequestFile
from ..UserManager.UserHelper import UserHelper
from .MaintenanceHelper import MaintenanceHelper
from ..LocationManager.LocationHelper import LocationHelper
from ..VendorManager.VendorHelper import VendorHelper
from ..InspectionTypeManager.InspectionTypeHelper import InspectionTypeHelper
from api.Models.DetailedUser import DetailedUser
from api.Models.asset_model import AssetModel
from ..Helper import HelperMethods
from datetime import datetime
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceUpdater():

    # --------------------------------------------------------------------------------------

    @staticmethod
    def batch_update_maintenance_request_post_creation(maintenance_request_objects, user):
        updated_maintenance_request_objects = []
        for maintenance_request_obj in maintenance_request_objects:
            maintenance_obj, created_by_response = MaintenanceUpdater.update_maintenance_request_post_creation(maintenance_request_obj, user)
            if created_by_response.status_code != status.HTTP_202_ACCEPTED:
                return None, created_by_response
            updated_maintenance_request_objects.append(maintenance_obj)
        return updated_maintenance_request_objects, Response(status=status.HTTP_202_ACCEPTED)

    # --------------------------------------------------------------------------------------
    
    @staticmethod
    def update_maintenance_request_post_creation(maintenance_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            maintenance_request_obj.created_by = detailed_user
            maintenance_request_obj.modified_by = detailed_user
            maintenance_request_obj.work_order = str(detailed_user.company.company_name).replace(' ', '-') + '-m-' + str(maintenance_request_obj.maintenance_id)
            maintenance_request_obj.save()
            return maintenance_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_4, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_4, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def construct_maintenance_file_instance(maintenance_obj, file_info, file_purpose, expiration_date, detailed_user):
        return MaintenanceRequestFile(
            maintenance_request=maintenance_obj,
            file_type=file_info.file_type,
            file_purpose=file_purpose,
            file_name=file_info.file_name,
            file_url=file_info.file_url,
            bytes=file_info.bytes,
            expiration_date=expiration_date,
            created_by=detailed_user
        )
    
    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_maintenance_request_modified_by(maintenance_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            maintenance_request_obj.modified_by = detailed_user
            maintenance_request_obj.save()
            return maintenance_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_4, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_4, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_maintenance_rule_post_creation(maintenance_rule_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            maintenance_rule_obj.created_by = detailed_user
            maintenance_rule_obj.modified_by = detailed_user
            maintenance_rule_obj.custom_id = str(detailed_user.company.company_name).replace(' ', '-') + "-mfr-" + str(maintenance_rule_obj.id)
            maintenance_rule_obj.save()
            return maintenance_rule_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_4, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_4, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_maintenance_rule_modified_by(maintenance_rule_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            maintenance_rule_obj.modified_by = detailed_user
            maintenance_rule_obj.save()
            return maintenance_rule_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_4, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_4, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def set_mileage_and_hours(maint_req, db_name):
        asset_obj = AssetModel.objects.using(db_name).get(pk=maint_req.VIN)
        maint_req.mileage = asset_obj.mileage
        maint_req.hours = asset_obj.hours
        return maint_req

    # --------------------------------------------------------------------------------------

    @staticmethod
    def delete_failed_maintenance_requests(maintenance_requests, db_name):
        for maint_req in maintenance_requests:
            MaintenanceRequestModel.objects.using(db_name).filter(maintenance_id=maint_req.maintenance_id).delete()

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_maintenance_fields(maintenance_entry, request_data, user):
        try:
            is_important = False
            if not len(str(request_data.get("location_id"))) == 0 and request_data.get("location_id") is not None:
                location, location_response = LocationHelper.get_location_by_id(request_data.get("location_id"), user.db_access)
                if location_response.status_code != status.HTTP_302_FOUND:
                    return maintenance_entry, location_response
                maintenance_entry.location = location
            if not len(str(request_data.get("assigned_vendor_id"))) == 0 and request_data.get("assigned_vendor_id") is not None:
                vendor, vendor_response = VendorHelper.get_vendor_by_id(request_data.get("assigned_vendor_id"), user.db_access)
                if vendor_response.status_code != status.HTTP_302_FOUND:
                    return maintenance_entry, vendor_response
                maintenance_entry.assigned_vendor = vendor
            if not len(str(request_data.get("inspection_type_id"))) == 0 and request_data.get("inspection_type_id") is not None:
                inspection_type, inspection_type_response = InspectionTypeHelper.get_inspection_type_by_id(request_data.get("inspection_type_id"), user.db_access)
                if inspection_type_response.status_code != status.HTTP_302_FOUND:
                    return maintenance_entry, inspection_type_response
                maintenance_entry.inspection_type = inspection_type

            if not len(str(request_data.get("in_house"))) == 0 and request_data.get("in_house") is not None:
                maintenance_entry.in_house = HelperMethods.validate_bool(request_data.get("in_house"))
            if not len(str(request_data.get("requested_delivery_date"))) == 0 and request_data.get("requested_delivery_date") is not None:
                maintenance_entry.requested_delivery_date = HelperMethods.datetime_string_to_datetime(request_data.get("requested_delivery_date"))
                is_important = True
            if not len(str(request_data.get("estimated_delivery_date"))) == 0 and request_data.get("estimated_delivery_date") is not None:
                maintenance_entry.estimated_delivery_date = HelperMethods.datetime_string_to_datetime(request_data.get("estimated_delivery_date"))
                is_important = True
            if not len(str(request_data.get("available_pickup_date"))) == 0 and request_data.get("available_pickup_date") is not None:
                maintenance_entry.available_pickup_date = HelperMethods.datetime_string_to_datetime(request_data.get("available_pickup_date")) 
                is_important = True
            if not len(str(request_data.get("vendor_contacted_date"))) == 0 and request_data.get("vendor_contacted_date") is not None:
                maintenance_entry.vendor_contacted_date = HelperMethods.datetime_string_to_datetime(request_data.get("vendor_contacted_date"))
            

            maintenance_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            return maintenance_entry, is_important, Response(status=status.HTTP_202_ACCEPTED)      
            
        except Exception as e:
            Logger.getLogger().error(CustomError.TUF_4, e)
            return None, Response(CustomError.get_full_error_json(CustomError.TUF_4, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def create_maintenance_entry(maintenance, detailed_user, db_name):
        
        asset = AssetHelper.get_asset_by_VIN(maintenance.get("VIN"), db_name)
        inspection_type, inspection_type_response = InspectionTypeHelper.get_inspection_type_by_code(maintenance.get("inspection_code"), db_name)
        location = LocationHelper.get_location_by_name(maintenance.get("location_name"), db_name)
        return MaintenanceRequestModel(
            VIN=asset,
            inspection_type=inspection_type,
            location=location,
            in_house=HelperMethods.validate_bool(maintenance.get("in_house")),
            created_by=detailed_user,
            modified_by=detailed_user,
            date_completed=HelperMethods.date_string_to_datetime(HelperMethods.ParseDateToDateField(maintenance.get("date_completed"))),
            estimated_delivery_date=HelperMethods.date_string_to_datetime(HelperMethods.ParseDateToDateField(maintenance.get("estimated_delivery_date"))),
            requested_delivery_date=HelperMethods.date_string_to_datetime(HelperMethods.ParseDateToDateField(maintenance.get("requested_delivery_date"))),
            vendor_contacted_date=HelperMethods.date_string_to_datetime(HelperMethods.ParseDateToDateField(maintenance.get("vendor_contacted_date"))),
            available_pickup_date=HelperMethods.date_string_to_datetime(HelperMethods.ParseDateToDateField(maintenance.get("available_pickup_date"))),
            vendor_email=maintenance.get("vendor_email"),
            mileage=maintenance.get("mileage"),
            hours=maintenance.get("hours"),
            status=MaintenanceRequestModel.complete
        )

    