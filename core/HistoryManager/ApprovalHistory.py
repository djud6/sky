from api.Models.approval_model_history import ApprovalModelHistory
from api.Models.approval import Approval
from ..ApprovalManager.ApprovalHelper import ApprovalHelper
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ApprovalHistory():

    @staticmethod
    def create_approval_record(approval_id, db_name):
        try:
            approval = Approval.objects.using(db_name).get(approval_id=approval_id)
            approval_entry = ApprovalHistory.generate_approval_history_entry(approval)
            approval_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_approval_record_from_obj(approval_obj):
        try:
            approval_entry = ApprovalHistory.generate_approval_history_entry(approval_obj)
            approval_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_approval_history_entry(approval):
        return ApprovalModelHistory(
            approval=approval,
            requesting_user=approval.requesting_user,
            approving_user=approval.approving_user,
            asset_request=approval.asset_request,
            maintenance_request=approval.maintenance_request,
            repair_request=approval.repair_request,
            title=approval.title,
            description=approval.description,
            deny_reason=approval.deny_reason,
            is_approved=approval.is_approved,
            location=approval.location
        )