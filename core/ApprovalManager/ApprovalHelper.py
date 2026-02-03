from rest_framework.response import Response
from rest_framework import status
from api.Models.approval import Approval
from api.Models.approval_model_history import ApprovalModelHistory
from api.Models.RolePermissions import RolePermissions
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ApprovalHelper():

    @staticmethod
    def select_related_to_approval(queryset):
        return queryset.select_related('requesting_user', 'approving_user', 'VIN', 'location', 'VIN__current_location', 'VIN__original_location', 'VIN__equipment_type__asset_type')

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_approval_by_id(approval_id, db_name):
        try:
            return Approval.objects.using(db_name).get(approval_id=approval_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.APRDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.APRDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_approval_for_daterange(start_date, end_date, db_name):
        return Approval.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_approval_history_for_daterange(start_date, end_date, db_name):
        return ApprovalModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_approvals_by_locations(locations, db_name):
        return Approval.objects.using(db_name).filter(location__in=locations)

    @staticmethod
    def get_approvals_by_transfer_ids(transfer_ids, db_name):
        return Approval.objects.using(db_name).filter(asset_transfer_request__in=transfer_ids)
        
    # ----------------------------------------------------------------------------------------------
    
    @staticmethod
    def user_can_approve(detailed_user_obj, approval_obj, valid_manager_emails):
        """
            If user is exec then they can approve/deny no matter what.
            If user is manager from the appropriate location and is not the user that created the approval request 
            then can approve/deny only if decision hasn't already been made. If the manager is the same user
            that made the previous approval decision, they are allowed to edit it.
        """
        if detailed_user_obj.role_permissions.role == RolePermissions.executive:
            return True
        elif detailed_user_obj.role_permissions.role == RolePermissions.manager:
            if detailed_user_obj.email != approval_obj.requesting_user.email:
                if detailed_user_obj.email in valid_manager_emails:
                    if approval_obj.approving_user == None or approval_obj.approving_user.email == detailed_user_obj.email:
                        return True
        return False