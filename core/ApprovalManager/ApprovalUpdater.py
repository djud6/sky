from rest_framework.response import Response
from rest_framework import status
from api.Models.approval import Approval
from api.Models.asset_transfer import AssetTransfer
from GSE_Backend.errors.ErrorDictionary import CustomError
from .ApprovalHelper import ApprovalHelper
from ..UserManager.UserHandler import UserHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..AssetRequestManager.AssetRequestHelper import AssetRequestHelper
from ..RepairManager.RepairHelper import RepairHelper
from ..MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from ..TransferManager.TransferHelper import TransferHelper
from ..Helper import HelperMethods
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ApprovalUpdater():

    @staticmethod
    def create_approval(request_data, user):
        try:
            approval_entry = ApprovalUpdater.create_approval_entry(request_data, user)
            approval_entry.save()
            return approval_entry, Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def create_approval_entry(request_data, user):
        asset = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), user.db_access)
        return Approval(
            VIN=asset,
            requesting_user=UserHelper.get_detailed_user_obj(user.email, user.db_access),
            title=request_data.get("title"),
            description=request_data.get("description"),
            location=asset.current_location
        )

    @staticmethod
    def set_fk_field(approval_obj, request_data, db_name):
        try:
            if not len(str(request_data.get("asset_request"))) == 0 and request_data.get("asset_request") is not None:
                asset_request, asset_request_response = AssetRequestHelper.get_asset_request_by_id(request_data.get("asset_request"), db_name)
                if asset_request_response.status_code != status.HTTP_302_FOUND:
                    return approval_obj, asset_request_response
                approval_obj.asset_request = asset_request
                approval_obj.save()
                return approval_obj, Response(status=status.HTTP_202_ACCEPTED)

            if not len(str(request_data.get("maintenance_request"))) == 0 and request_data.get("maintenance_request") is not None:
                maintenance_request, maintenance_request_response = MaintenanceHelper.get_maintenance_request_by_id(request_data.get("maintenance_request"), db_name)
                if maintenance_request_response.status_code != status.HTTP_302_FOUND:
                    return approval_obj, maintenance_request_response
                approval_obj.maintenance_request = maintenance_request
                approval_obj.save()
                return approval_obj, Response(status=status.HTTP_202_ACCEPTED)

            if not len(str(request_data.get("repair_request"))) == 0 and request_data.get("repair_request") is not None:
                repair_request, repair_request_response = RepairHelper.get_repair_request_by_id(request_data.get("repair_request"), db_name)
                if repair_request_response.status_code != status.HTTP_302_FOUND:
                    return approval_obj, repair_request_response
                approval_obj.repair_request = repair_request
                approval_obj.save()
                return approval_obj, Response(status=status.HTTP_202_ACCEPTED)

            if not len(str(request_data.get("asset_transfer_request"))) == 0 and request_data.get("asset_transfer_request") is not None:
                transfer_request, transfer_request_response = TransferHelper.get_transfer_by_id(request_data.get("asset_transfer_request"), db_name)
                if transfer_request_response.status_code != status.HTTP_302_FOUND:
                    return approval_obj, transfer_request_response
                approval_obj.asset_transfer_request = transfer_request
                approval_obj.save()
                return approval_obj, Response(status=status.HTTP_202_ACCEPTED)

            else:
                #ApprovalUpdater.delete_approval_entry_by_id(approval_obj)
                Logger.getLogger().error(CustomError.AMFK_0)
                return None, Response(CustomError.get_full_error_json(CustomError.AMFK_0), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            #ApprovalUpdater.delete_approval_entry_by_id(approval_obj)
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def set_approval_status(approval_obj, request_data, detailed_user_obj, db_name):
        try:
            approval_obj.is_approved = HelperMethods.validate_bool(request_data.get("is_approved"))
            approval_obj.approving_user = detailed_user_obj
            if not len(str(request_data.get("deny_reason"))) == 0 and request_data.get("deny_reason") is not None:
                approval_obj.deny_reason = str(request_data.get("deny_reason"))
            
            approval_obj.save()

            if approval_obj.asset_request:
                #This will be updated later in the development
                pass
            elif approval_obj.maintenance_request:
                #This will be updated later in the development
                pass
            elif approval_obj.repair_request:
                #This will be updated later in the development
                pass
            elif approval_obj.asset_transfer_request:
                trans_id = approval_obj.asset_transfer_request.asset_transfer_id
                transfer_obj, transfer_request_response = TransferHelper.get_transfer_by_id(trans_id, db_name)
                if transfer_request_response.status_code != status.HTTP_302_FOUND:
                    return transfer_request_response
                if approval_obj.is_approved==1:
                    transfer_obj.status = AssetTransfer.approved
                else:
                    transfer_obj.status = AssetTransfer.denied
                transfer_obj.save()               
            return approval_obj, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete_approval_entry(approval_obj):
        approval_obj.delete()