from core.IssueManager.IssueHelper import IssueHelper
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_issue import AssetIssueModel
from api.Models.asset_issue_file import AssetIssueFileModel
from ..UserManager.UserHelper import UserHelper
from ..AccidentManager.AccidentHelper import AccidentHelper
from ..RepairManager.RepairHelper import RepairHelper
from api.Models.DetailedUser import DetailedUser
from core.FileManager.ImageManager import ImageManager
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class IssueUpdater():

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_issue_post_creation(issue_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            issue_obj.created_by = detailed_user
            issue_obj.modified_by = detailed_user
            issue_obj.custom_id = str(detailed_user.company.company_name).replace(' ', '-') + "-i-" + str(issue_obj.issue_id)
            issue_obj.save()
            return issue_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_3, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_3, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_issue_modified_by(issue_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            issue_obj.modified_by = detailed_user
            issue_obj.save()
            return issue_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_3, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_3, e), status=status.HTTP_400_BAD_REQUEST)


    # --------------------------------------------------------------------------------------

    @staticmethod
    def create_issue_file_record(issue_obj, file_infos, dbName):
        try:
            entries = list()
            for file_info in file_infos:
                entries.append(IssueUpdater.construct_issue_file_model_instance(issue_obj, file_info))
            AssetIssueFileModel.objects.using(dbName).bulk_create(entries)

            return True
        
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    # --------------------------------------------------------------------------------------

    @staticmethod
    def construct_issue_file_model_instance(issue_obj, file_info):
        return AssetIssueFileModel(
            issue=issue_obj,
            file_type=file_info.file_type,
            file_name=file_info.file_name,
            file_url=file_info.file_url,
            bytes=file_info.bytes
        )

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_issue_fields(issue_entry, request_data, user):
        try:
            is_important = False
            if not len(str(request_data.get("issue_category_id"))) == 0 and request_data.get("issue_category_id") is not None:
                category, category_response = IssueHelper.get_issue_category_by_id(request_data.get("issue_category_id"), user.db_access)
                if category_response.status_code != status.HTTP_302_FOUND:
                    return issue_entry, category_response
                issue_entry.category = category
            
            if not len(str(request_data.get("accident_id"))) == 0 and request_data.get("accident_id") is not None:
                accident, accident_response = AccidentHelper.get_accident_by_id(request_data.get("accident_id"), user.db_access)
                if accident_response.status_code != status.HTTP_302_FOUND:
                    return issue_entry, accident_response
                issue_entry.accident_id = accident

            if not len(str(request_data.get("repair_id"))) == 0 and request_data.get("repair_id") is not None:
                repair, repair_response = RepairHelper.get_repair_request_by_id(request_data.get("repair_id"), user.db_access)
                if repair_response.status_code != status.HTTP_302_FOUND:
                    return issue_entry, repair_response
                issue_entry.repair_id = repair

            if not len(str(request_data.get("issue_details"))) == 0 and request_data.get("issue_details") is not None:
                issue_entry.issue_details = request_data.get("issue_details").strip()
            if not len(str(request_data.get("issue_title"))) == 0 and request_data.get("issue_title") is not None:
                issue_entry.issue_title = request_data.get("issue_title").strip()
            if not len(str(request_data.get("issue_type"))) == 0 and request_data.get("issue_type") is not None:
                issue_entry.issue_type = request_data.get("issue_type").strip()
            if not len(str(request_data.get("issue_result"))) == 0 and request_data.get("issue_result") is not None:
                issue_entry.issue_result = request_data.get("issue_result").strip()
                is_important = True

            issue_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)       

            return issue_entry, is_important, Response(status=status.HTTP_202_ACCEPTED) 

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_8, e))
            return issue_entry, is_important, Response(CustomError.get_full_error_json(CustomError.TUF_8, e), status=status.HTTP_400_BAD_REQUEST)

