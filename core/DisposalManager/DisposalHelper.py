from core.AssetManager.AssetHelper import AssetHelper
from core.Helper import HelperMethods
from core.FileManager.PdfManager import PdfManager
from api.Models.asset_disposal_file import AssetDisposalFile
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_disposal_history import AssetDisposalModelHistory
from api.Models.RolePermissions import RolePermissions
from ..UserManager.UserHelper import UserHelper
from ..FileManager.FileHelper import FileHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..HistoryManager.DisposalHistory import DisposalHistory
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
import logging
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
from api.Models.DetailedUser import DetailedUser
from core.RepairManager.RepairHelper import RepairHelper

import sys

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DisposalHelper():

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_disposal_ser_context(disposal_id_list, db_name):
        # Get disposal files and secure urls
        container_name = "disposal"
        disposal_files = AssetDisposalFile.objects.using(db_name).filter(disposal__in=disposal_id_list).order_by('-file_id').values()
        refurbish_work_orders = RepairHelper.get_all_refurbishment_work_orders(db_name).values('work_order', 'disposal__custom_id')
        for disposal_file in disposal_files:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, container_name, disposal_file.get('file_url'))
            disposal_file['file_url'] = secure_file_url
        return {
            'disposal_files': disposal_files,
            'refurbish_work_orders' : refurbish_work_orders
            }

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def select_related_to_disposal(queryset):
        return queryset.select_related('VIN__equipment_type__asset_type', 'VIN__equipment_type__manufacturer', 'VIN__equipment_type', 'location', 'VIN__current_location', 'VIN__original_location', 'VIN__fuel', 'VIN', 'created_by', 'modified_by')

    # ----------------------------------------------------------------------------------------------

    # This method will take a disposals qs and filter it to only show disposals relevant to user
    @staticmethod
    def filter_disposal_for_user(disposal_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return disposal_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return disposal_qs.filter(location__in=user_locations)

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def is_status_new_by_id(db_name, _id, status):
        asset_disposal = AssetDisposalModel.objects.using(db_name).get(pk=_id)
        if status == asset_disposal.status:
            return False
        return True

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def is_status_new_by_obj(asset_disposal, status):
        if str(status).lower() == str(asset_disposal.status).lower():
            return False
        return True

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def disposal_exists(disposal_id, db_name):
        return AssetDisposalModel.objects.using(db_name).filter(pk=disposal_id).exists()

    @staticmethod
    def asset_disposal_entry_exists(db_name, _id):
        return AssetDisposalModel.objects.using(db_name).filter(pk=_id).exists()

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_disposal_request_by_id(disposal_id, db_name):
        try:
            return AssetDisposalModel.objects.using(db_name).get(pk=disposal_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.DDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.DDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_disposal_request_by_custom_id(custom_disposal_id, db_name):
        try:
            return AssetDisposalModel.objects.using(db_name).get(custom_id=custom_disposal_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.DDNE_1, e))
            return None, Response(CustomError.get_full_error_json(CustomError.DDNE_1, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_asset_disposals(db_name):
        return AssetDisposalModel.objects.using(db_name).select_related('created_by', 'modified_by').all()

    @staticmethod
    def get_latest_asset_disposals_by_vin(VIN, db_name):
        return AssetDisposalModel.objects.using(db_name).select_related('created_by', 'modified_by').filter(VIN=VIN).order_by('-id').values('id', 'VIN', 'status', 'disposal_type')

    @staticmethod
    def get_latest_asset_disposals(db_name):
        return AssetDisposalModel.objects.using(db_name).select_related('created_by', 'modified_by').order_by('-id').values('id', 'VIN', 'status', 'disposal_type')

    @staticmethod
    def get_disposal_file_entries_for_daterange(start_date, end_date, db_name):
        return AssetDisposalFile.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_disposals_for_daterange(start_date, end_date, db_name):
        return AssetDisposalModel.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_disposal_history_for_daterange(start_date, end_date, db_name):
        return AssetDisposalModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_disposal_location(disposal_obj):
        if disposal_obj.location != None:
            return disposal_obj.location
        else: # If None return 0 as there are no location IDs that are 0
            return 0

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def check_valid_scrap(request_data):
        return request_data.get("is_stripped") != None

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_disposal_history_error(disposal_type):
        errors = {
            "company directed sale": CustomError.MHF_0,
            "auction": CustomError.MHF_1,
            "repurpose": CustomError.MHF_2,
            "scrap": CustomError.MHF_3,
            "donation": CustomError.MHF_4,
            "trade in": CustomError.MHF_5,
            "transfer": CustomError.MHF_6
        }
        return errors[disposal_type]

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_trade_ins(db_name):
        return AssetDisposalModel.objects.using(db_name).filter(disposal_type="trade in")
        
    # ----------------------------------------------------------------------------------------------        

    def get_write_offs(db_name):
        return AssetDisposalModel.objects.using(db_name).filter(disposal_type="write-off")

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def validate_disposal_status(status):
        if status in dict(AssetDisposalModel.disposal_status_choices):
            return True
        return False

    # ----------------------------------------------------------------------------------------------

    # This method insures that all provided files have a corresponding info json and that the required file types are provided
    @staticmethod
    def required_files_included(required_files_purposes, provided_file_specs, provided_files):
        found_info_count = 0
        required_purposes_dict = {required_files_purposes[i]: 0 for i in range(0, len(required_files_purposes))}

        for _file in provided_files:
            for file_info in provided_file_specs:
                if file_info.get("file_name") == _file.name:
                    found_info_count += 1
                    if file_info.get("purpose") in required_files_purposes:
                        required_purposes_dict[file_info.get("purpose")] = 1

        if found_info_count < len(provided_files):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADUF_1))
            return Response(CustomError.get_full_error_json(CustomError.ADUF_1), status=status.HTTP_400_BAD_REQUEST)

        if sum(required_purposes_dict.values()) < len(required_files_purposes):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADUF_2))
            return Response(CustomError.get_full_error_json(CustomError.ADUF_2), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_allowed_file_types_for_purpose(purpose):
        # ["application/pdf", "text/plain", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.bill_of_sale:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.method_of_payment:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.letter_of_release:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.insurance:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.total_loss_declaration:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.tax_receipt:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.invoice:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.proceeds:
            return ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetDisposalFile.other_support:
            return ["application/pdf", "text/plain", "image/jpeg", "image/png", "image/heic", "image/heif"]
        return []

    # ----------------------------------------------------------------------------------------------
    
    @staticmethod
    def validate_files(required_file_purposes, file_info, files):
        required_files_response = DisposalHelper.required_files_included(required_file_purposes, file_info, files)
        if required_files_response.status_code != status.HTTP_200_OK:
            return required_files_response

        for _file in files:
            file_purpose = ""
            for info in file_info:
                if info.get("file_name") == _file.name:
                    file_purpose = info.get("purpose").lower()

            # Check if file type is valid
            valid_issue_file_types = DisposalHelper.get_allowed_file_types_for_purpose(file_purpose)
            if not FileHelper.verify_file_is_accepted_type(_file, valid_issue_file_types):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1))
                return Response(CustomError.get_full_error_json(CustomError.FUF_1), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK) 

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def generate_appropriate_notification_email(disposal_obj, company_obj, trigger, user, is_update=False):
        disposal_type = str(disposal_obj.disposal_type).lower()
        
        if disposal_type == AssetDisposalModel.scrap:
            notification_config, resp = NotificationHelper.get_notification_config_by_name("New Scrap Disposal", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                    notification_config.triggers is None or (
                        trigger in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                return (
                    PdfManager.gen_scrap_disposal_report(disposal_obj, company_obj, notification_config, user, is_update=is_update),
                    notification_config
                )
            return None
        
        if disposal_type == AssetDisposalModel.donate:
            notification_config, resp = NotificationHelper.get_notification_config_by_name("New Donation Disposal", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                    notification_config.triggers is None or (
                        trigger in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                return (
                    PdfManager.gen_donate_disposal_report(disposal_obj, company_obj, notification_config, user, is_update=is_update),
                    notification_config
                )
            return None
        
        if disposal_type == AssetDisposalModel.auction:
            notification_config, resp = NotificationHelper.get_notification_config_by_name("New Auction Disposal", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                    notification_config.triggers is None or (
                        trigger in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                return (
                    PdfManager.gen_auction_disposal_report(disposal_obj, company_obj, notification_config, user, is_update=is_update),
                    notification_config
                )
            return None
        
        return "Failed to generate asset disposal report due to incorrect disposal type. Please contact administrator."

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def update_disposal_dict(request_data, db_name):
        request_data["location"] = AssetHelper.get_asset_location_id(request_data.get("VIN"), db_name)
        request_data["disposal_type"] = request_data.get("disposal_type").lower()
        return request_data

    # ----------------------------------------------------------------------------------------------

    # expects a sorted list of InMemoryUploadedFile objects
    # the list must be sorted in descending order of size
    @staticmethod
    def prune_files_for_email(files, size_in_mb):
        # if there are no files or if the size is 0, return an empty list
        if not (files and size_in_mb):
            return []

        current_file_size = DisposalHelper.bytes_to_megabytes(sum([file.size for file in files]))

        pruned_files = files[:]
        # if the files in the list are less than the given size, return the entire list
        if current_file_size <= size_in_mb:
            return files

        # while the list is larger than the given size, knock off the largest file and check the size
        # do this repeatedly until the list is smaller than the given size
        while current_file_size > size_in_mb:
            current_file_size -= DisposalHelper.bytes_to_megabytes(pruned_files[0].size)
            pruned_files = pruned_files[1:] if len(pruned_files) > 1 else []

        return pruned_files

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_files_for_disposal(files, db_access, asset_vin):
        unique_files = []
        for f in files:
            unique_files.append((f.name, f.size))

        # function to remove the files already in memory from the queryset aswell as any duplicates within the queryset
        # the latest of any duplicates will be left in the final set of files
        def remove_duplicates(file):
            if (file.get('file_name'), file.get('bytes')) in unique_files:
                return False
            unique_files.append((file.get('file_name'), file.get('bytes')))
            return True

        asset_files_qs = list(AssetHelper.get_asset_files_by_vin(asset_vin, db_access).order_by('-file_id').values())
        asset_files_qs = list(filter(remove_duplicates, asset_files_qs))
        current_file_size = DisposalHelper.bytes_to_megabytes(sum([file.size for file in files]))
        # calculate the space left in the email after including the files in the request
        # also, ensure that the value does not go below zero
        space_left = max(25 - current_file_size, 0)
        asset_files = AssetHelper.get_asset_files_from_blob(asset_files_qs, db_access)
        asset_files = DisposalHelper.prune_files_for_email(asset_files, space_left)
        return files + asset_files

    @staticmethod
    def bytes_to_megabytes(bytes):
        return bytes / 10**6
