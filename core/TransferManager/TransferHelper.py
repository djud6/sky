from api import Approvals
from rest_framework.response import Response
from rest_framework import status

from core.ApprovalManager.ApprovalHelper import ApprovalHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..UserManager.UserHelper import UserHelper
from api.Models.asset_model import AssetModel
from api.Models.asset_transfer import AssetTransfer
from api.Models.transfer_file import TransferFile
from api.Models.asset_transfer_history import AssetTransferModelHistory
from api.Models.DetailedUser import DetailedUser
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.db.models import Q
from api.Models.approval import Approval
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class TransferHelper():

    @staticmethod
    def select_related_to_transfer(queryset):
        return queryset.select_related('created_by', 'modified_by', 'original_location', 'VIN__current_location', 'VIN__original_location', 'destination_location', 'VIN__department')

    @staticmethod
    def get_transfer_ser_context(transfer_id_list, db_name):
        # Get transfer files and secure urls
        approvals = ApprovalHelper.get_approvals_by_transfer_ids(transfer_id_list, db_name).values('asset_transfer_request', 'approving_user__email')
        container_name = "transfer"
        transfer_files = TransferFile.objects.using(db_name).filter(transfer__in=transfer_id_list).order_by('-file_id').values()
        for transfer_file in transfer_files:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, container_name, transfer_file.get('file_url'))
            transfer_file['file_url'] = secure_file_url
        return {
            'transfer_files': transfer_files,
            'approvals': approvals
            }

    # --------------------------------------------------------------------------------------------------

    @staticmethod
    def is_status_valid(status):
        if status in dict(AssetTransfer.transfer_status_choices):
            return True
        return False

    @staticmethod
    def is_status_new(transfer_obj, status):
        if str(status) != str(transfer_obj.status):
            return True
        return False

    @staticmethod
    def is_condition_valid(condition):
        if condition in dict(AssetTransfer.condition_choices):
            return True
        return False

    @staticmethod
    def get_transfer_by_id(transfer_id, db_name):
        try:
            return AssetTransfer.objects.using(db_name).get(asset_transfer_id=transfer_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ATDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ATDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_transfer_by_custom_id(custom_transfer_id, db_name):
        try:
            return AssetTransfer.objects.using(db_name).get(custom_id=custom_transfer_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ATDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ATDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def validate_purpose(file_purpose):
        if file_purpose in dict(TransferFile.file_purpose_choices):
            return True
        return False

    @staticmethod
    def get_user_location_related_transfers(user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            user_locations = detailed_user.location.values_list('location_id', flat=True)
            #print(user_locations)

            vins_in_user_locations = AssetModel.objects.using(user.db_access).filter(current_location__in=user_locations).values_list('VIN', flat=True)
            #print(vins_in_user_locations)

            vins_with_transfers = AssetTransfer.objects.using(user.db_access).values_list('VIN', flat=True)
            #print(vins_with_transfers)

            vins_in_user_location_with_transfers = AssetModel.objects.using(user.db_access).filter(VIN__in=vins_in_user_locations).filter(VIN__in=vins_with_transfers).values_list('VIN', flat=True)
            #print(vins_in_user_location_with_transfers)

            user_related_transfers = AssetTransfer.objects.using(user.db_access).filter(Q(destination_location__in=user_locations) | Q(VIN__in=vins_in_user_location_with_transfers))
            #print(user_related_transfers.values_list('VIN', flat=True))

            return user_related_transfers, Response(status=status.HTTP_302_FOUND)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_user_location_related_transfers_by_vin(user, _vin):
        qs, response = TransferHelper.get_user_location_related_transfers(user)
        if(response.status_code != status.HTTP_302_FOUND):
            return None, response  
        updated_qs = qs.filter(VIN=_vin)
        return updated_qs, Response(status=status.HTTP_200_OK)

    
    @staticmethod
    def get_asset_transfers(db_name):
        return AssetTransfer.objects.using(db_name).all()

    
    @staticmethod
    def get_transfer_by_VIN(VIN, db_name):
        return AssetTransfer.objects.using(db_name).get(VIN=VIN)
    
    @staticmethod
    def get_latest_asset_transfer_by_vin(VIN, db_name):
        return AssetTransfer.objects.using(db_name).select_related('created_by', 'modified_by').filter(VIN=VIN).order_by('-asset_transfer_id').values('asset_transfer_id', 'VIN', 'status')
    
    @staticmethod
    def get_latest_asset_transfer(db_name):
        return AssetTransfer.objects.using(db_name).select_related('created_by', 'modified_by').order_by('-asset_transfer_id').values('asset_transfer_id', 'VIN', 'status')
       
    @staticmethod
    def get_executives_emails(db_name):
        return DetailedUser.objects.using(db_name).filter(role_permissions__role='executive').values_list('email', flat=True)

    @staticmethod
    def get_transfer_file_entries_for_daterange(start_date, end_date, db_name):
        return TransferFile.objects.using(db_name).filter(file_created__range=[start_date, end_date])

    @staticmethod
    def get_transfers_for_daterange(start_date, end_date, db_name):
        return AssetTransfer.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_transfer_history_for_daterange(start_date, end_date, db_name):
        return AssetTransferModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])
