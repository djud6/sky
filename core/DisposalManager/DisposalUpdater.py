from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_disposal_history import AssetDisposalModelHistory
from api.Models.asset_disposal_file import AssetDisposalFile
from .DisposalHelper import DisposalHelper
from ..UserManager.UserHelper import UserHelper
from ..VendorManager.VendorHelper import VendorHelper
from ..Helper import HelperMethods
from api.Models.DetailedUser import DetailedUser
from django.utils import timezone
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DisposalUpdater():

    # --------------------------------------------------------------------------------------

    #Edits disposal status for a given disposal ID
    @staticmethod
    def edit_disposal_status(asset_disposal, dis_status):
        if DisposalHelper.validate_disposal_status(str(dis_status).lower()):
            asset_disposal.status = str(dis_status).lower()
            asset_disposal.save()
            return asset_disposal, Response(status=status.HTTP_202_ACCEPTED)
        Logger.getLogger().error(CustomError.IADS_0)
        return asset_disposal, Response(CustomError.get_full_error_json(CustomError.IADS_0), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_disposal_request_post_creation(disposal_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            disposal_request_obj.created_by = detailed_user
            disposal_request_obj.modified_by = detailed_user
            disposal_request_obj.custom_id = str(detailed_user.company.company_name).replace(' ', '-') + "-d-" + str(disposal_request_obj.id)
            disposal_request_obj.save()
            return disposal_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_2, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_2, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_disposal_request_modified_by(disposal_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            disposal_request_obj.modified_by = detailed_user
            disposal_request_obj.save()
            return disposal_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_2, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_2, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def delete_failed_disposal_requests(disposal_requests, db_name):
        for disposal in disposal_requests:
            AssetDisposalModel.objects.using(db_name).filter(pk=disposal.id).delete()

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_disposal_fields(disposal_entry, request_data, user):
        try:
            is_important = False
            if not len(str(request_data.get("vendor_id"))) == 0 and request_data.get("vendor_id") is not None:
                vendor, vendor_response = VendorHelper.get_vendor_by_id(request_data.get("vendor_id"), user.db_access)
                if vendor_response.status_code != status.HTTP_302_FOUND:
                    return disposal_entry, vendor_response
                disposal_entry.vendor = vendor

            if not len(str(request_data.get("vendor_contacted_date"))) == 0 and request_data.get("vendor_contacted_date") is not None:
                disposal_entry.vendor_contacted_date = HelperMethods.datetime_string_to_datetime(request_data.get("vendor_contacted_date"))
            if not len(str(request_data.get("estimated_pickup_date"))) == 0 and request_data.get("estimated_pickup_date") is not None:
                disposal_entry.estimated_pickup_date = HelperMethods.datetime_string_to_datetime(request_data.get("estimated_pickup_date"))
                is_important = True
            if not len(str(request_data.get("accounting_contacted_date"))) == 0 and request_data.get("accounting_contacted_date") is not None:
                disposal_entry.accounting_contacted_date = HelperMethods.datetime_string_to_datetime(request_data.get("accounting_contacted_date"))
            if not len(str(request_data.get("interior_condition"))) == 0 and request_data.get("interior_condition") is not None:
                disposal_entry.interior_condition = request_data.get("interior_condition").strip()
            if not len(str(request_data.get("interior_condition_details"))) == 0 and request_data.get("interior_condition_details") is not None:
                disposal_entry.interior_condition_details = request_data.get("interior_condition_details").strip()
            if not len(str(request_data.get("exterior_condition"))) == 0 and request_data.get("exterior_condition") is not None:
                disposal_entry.exterior_condition = request_data.get("exterior_condition").strip()
            if not len(str(request_data.get("exterior_condition_details"))) == 0 and request_data.get("exterior_condition_details") is not None:
                disposal_entry.exterior_condition_details = request_data.get("exterior_condition_details").strip()
            if not len(str(request_data.get("disposal_reason"))) == 0 and request_data.get("disposal_reason") is not None:
                disposal_entry.disposal_reason = request_data.get("disposal_reason").strip()
            if not len(str(request_data.get("replacement_reason"))) == 0 and request_data.get("replacement_reason") is not None:
                disposal_entry.replacement_reason = request_data.get("replacement_reason").strip()
                
            if not len(str(request_data.get("is_stripped"))) == 0 and request_data.get("is_stripped") is not None:
                disposal_entry.is_stripped = HelperMethods.validate_bool(request_data.get("is_stripped"))
            if not len(str(request_data.get("refurbished"))) == 0 and request_data.get("refurbished") is not None:
                disposal_entry.refurbished = HelperMethods.validate_bool(request_data.get("refurbished"))

            disposal_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            return disposal_entry, is_important, Response(status=status.HTTP_202_ACCEPTED)     

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_6, e))
            return disposal_entry, Response(CustomError.get_full_error_json(CustomError.TUF_6, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------
    
    @staticmethod
    def construct_disposal_file_instance(disposal_obj, file_info, file_purpose, expiration_date, detailed_user):
        return AssetDisposalFile(
            disposal=disposal_obj,
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
    def update_vendor_contacted_date(disposal_obj):
        disposal_obj.vendor_contacted_date = timezone.now()
        return disposal_obj

    # --------------------------------------------------------------------------------------
