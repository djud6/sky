from rest_framework.response import Response
from rest_framework import status
from api.Models.repairs import RepairsModel
from api.Models.asset_model import AssetModel
from api.Models.asset_issue import AssetIssueModel
from api.Models.accident_report import AccidentModel
from api.Models.repair_file import RepairFile
from ..UserManager.UserHelper import UserHelper
from ..LocationManager.LocationHandler import LocationHelper
from ..VendorManager.VendorHelper import VendorHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
from datetime import datetime
import logging

class Logger():
    
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RepairUpdater:

    # --------------------------------------------------------------------------------------

    @staticmethod
    def delete_repair_by_id(repair_id, db_name):
        RepairsModel.objects.using(db_name).filter(repair_id=repair_id).delete()

    # --------------------------------------------------------------------------------------

    # Sets mileage of repair dict to the most current value in the corresponding asset obj
    @staticmethod
    def set_repair_dict_mileage(request, repair_dict):
        data = repair_dict
        asset_obj = AssetModel.objects.get(VIN=data.get("VIN"))
        data["mileage"] = asset_obj.mileage
        return data

    # --------------------------------------------------------------------------------------

    # Sets hours of repair dict to the most current value in the corresponding asset obj
    @staticmethod
    def set_repair_dict_hours(request, repair_dict):
        data = repair_dict
        asset_obj = AssetModel.objects.get(VIN=data.get("VIN"))
        data["hours"] = asset_obj.hours
        return data

    # --------------------------------------------------------------------------------------

    # Sets mileage and hours of repair dict to the most current value in the corresponding asset obj
    @staticmethod
    def set_repair_dict_mileage_and_hours(repair_dict):
        data = repair_dict
        asset_obj = AssetModel.objects.get(VIN=data.get("VIN"))
        data["mileage"] = asset_obj.mileage
        data["hours"] = asset_obj.hours
        return data

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_repair_request_post_creation(repair_request_obj, detailed_user):
        try:
            repair_request_obj.created_by = detailed_user
            repair_request_obj.modified_by = detailed_user
            repair_request_obj.work_order = str(detailed_user.company.company_name).replace(' ', '-') + "-r-" + str(repair_request_obj.repair_id)
            repair_request_obj.location = repair_request_obj.VIN.current_location
            repair_request_obj.save()
            return repair_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_5, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_5, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_repair_request_modified_by(repair_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            repair_request_obj.modified_by = detailed_user
            repair_request_obj.save()
            return repair_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_5, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_5, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_issues(_repair_id, _status, db_name):
        issues = AssetIssueModel.objects.filter(repair_id=_repair_id)
        accident_ids = issues.values_list('accident_id', flat=True)
        issues_list = []
        if issues:
            for issue in issues.iterator():
                issue.is_resolved = HelperMethods.validate_bool(_status)
                issue.issue_updated = datetime.utcnow()
                issues_list.append(issue)
                if issue.is_resolved:
                    date_now = datetime.utcnow()
                else:
                    date_now = None
        else:
            date_now = datetime.utcnow() 
        AssetIssueModel.objects.using(db_name).bulk_update(issues_list, ['is_resolved', 'issue_updated'])
        AccidentModel.objects.using(db_name).filter(accident_id__in=accident_ids).update(date_returned_to_service=date_now)

    # --------------------------------------------------------------------------------------

    #This method will update the asset down time for a collection of assets
    @staticmethod
    def update_repair_downtime(repairs, db_name):
        now = datetime.utcnow()
        repairs_list = []
        for repair in repairs:
            if(repair.status == RepairsModel.complete):
                pass
            else: # action is not completed
                delta = HelperMethods.get_datetime_delta(start=repair.date_created, end=now, delta_format="hours")
                repair.down_time = delta
            repairs_list.append(repair)

        RepairsModel.objects.using(db_name).bulk_update(repairs_list, ['down_time'])

        return repairs

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_repair_fields(repair_entry, request_data, user):
        try:
            is_important = False
            if not len(str(request_data.get("location_id"))) == 0 and request_data.get("location_id") is not None:
                location, location_response = LocationHelper.get_location_by_id(request_data.get("location_id"), user.db_access)
                if location_response.status_code != status.HTTP_302_FOUND:
                    return repair_entry, location_response
                repair_entry.location = location
            if not len(str(request_data.get("vendor_id"))) == 0 and request_data.get("vendor_id") is not None:
                vendor, vendor_response = VendorHelper.get_vendor_by_id(request_data.get("vendor_id"), user.db_access)
                if vendor_response.status_code != status.HTTP_302_FOUND:
                    return repair_entry, vendor_response
                repair_entry.vendor = vendor
            if not len(str(request_data.get("disposal_id"))) == 0 and request_data.get("disposal_id") is not None:
                disposal, disposal_response = DisposalHelper.get_disposal_request_by_id(request_data.get("disposal_id"), user.db_access)
                if disposal_response.status_code != status.HTTP_302_FOUND:
                    return repair_entry, disposal_response
                repair_entry.disposal = disposal
            
            if not len(str(request_data.get("in_house"))) == 0 and request_data.get("in_house") is not None:
                repair_entry.in_house = HelperMethods.validate_bool(request_data.get("in_house"))
            if not len(str(request_data.get("description"))) == 0 and request_data.get("description") is not None:
                repair_entry.description = request_data.get("description").strip()
            if not len(str(request_data.get("is_refurbishment"))) == 0 and request_data.get("is_refurbishment") is not None:
                repair_entry.is_refurbishment = HelperMethods.validate_bool(request_data.get("is_refurbishment"))
            if not len(str(request_data.get("requested_delivery_date"))) == 0 and request_data.get("requested_delivery_date") is not None:
                repair_entry.requested_delivery_date = HelperMethods.datetime_string_to_datetime(request_data.get("requested_delivery_date"))
            if not len(str(request_data.get("estimated_delivery_date"))) == 0 and request_data.get("estimated_delivery_date") is not None:
                repair_entry.estimated_delivery_date = HelperMethods.datetime_string_to_datetime(request_data.get("estimated_delivery_date"))
                is_important = True
            if not len(str(request_data.get("available_pickup_date"))) == 0 and request_data.get("available_pickup_date") is not None:
                repair_entry.available_pickup_date = HelperMethods.datetime_string_to_datetime(request_data.get("available_pickup_date"))
            if not len(str(request_data.get("vendor_contacted_date"))) == 0 and request_data.get("vendor_contacted_date") is not None:
                repair_entry.vendor_contacted_date = HelperMethods.datetime_string_to_datetime(request_data.get("vendor_contacted_date"))

            if not len(str(request_data.get("is_urgent"))) == 0 and request_data.get("is_urgent") is not None:
                repair_entry.is_urgent = HelperMethods.validate_bool(request_data.get("is_urgent")) 

            repair_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)        

            return repair_entry, is_important, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_3, e))
            return repair_entry, is_important, Response(CustomError.get_full_error_json(CustomError.TUF_3, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def construct_repair_file_instance(repair_object, file_info, file_purpose, expiration_date, detailed_user):
        return RepairFile(
            repair=repair_object,
            file_type=file_info.file_type,
            file_purpose=file_purpose,
            file_name=file_info.file_name,
            file_url=file_info.file_url,
            bytes=file_info.bytes,
            expiration_date=expiration_date,
            created_by=detailed_user
        )