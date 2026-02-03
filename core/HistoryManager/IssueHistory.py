from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_issue_history import AssetIssueModelHistory
from api.Models.asset_issue import AssetIssueModel
from api.Models.asset_log import AssetLog
from ..HistoryManager.AssetHistory import AssetHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class IssueHistory():

    @staticmethod
    def create_issue_record(issue_id, db_name):
        try:
            issue = AssetIssueModel.objects.using(db_name).get(issue_id=issue_id)
            issue_history_entry = IssueHistory.generate_issuehistory_entry(issue)
            issue_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_issue_record_by_obj(issue):
        try:
            issue_history_entry = IssueHistory.generate_issuehistory_entry(issue)
            issue_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_issuehistory_entry(issue):
        return AssetIssueModelHistory(
            issue=issue,
            custom_id=issue.custom_id,
            issue_details=issue.issue_details,
            issue_title=issue.issue_title,
            issue_type=issue.issue_type,
            accident=issue.accident_id,
            repair=issue.repair_id,
            issue_result=issue.issue_result,
            is_resolved=issue.is_resolved,
            modified_by=issue.modified_by,
            location=issue.location
        )

    @staticmethod
    def create_issue_event_log(issue_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(issue_obj.VIN, AssetLog.issue, issue_obj.custom_id, issue_obj.modified_by, description, issue_obj.location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_4, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_4, e), status=status.HTTP_400_BAD_REQUEST)