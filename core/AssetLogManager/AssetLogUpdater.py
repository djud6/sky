from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_log import AssetLog
from ..UserManager.UserHelper import UserHelper
from ..AssetManager.AssetHelper import AssetHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetLogUpdater():

    @staticmethod
    def create_asset_log_comment(request_data, user):
        try:
            sender_detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            asset_log_entry = AssetLogUpdater.create_asset_log_comment_entry(request_data, user, sender_detailed_user)
            asset_log_entry.save()
            return asset_log_entry, Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_asset_log_comment_entry(request_data, user, sender_detailed_user):
        return AssetLog(
            VIN=AssetHelper.get_asset_by_VIN(request_data.get("VIN"), user.db_access),
            log_type=AssetLog.comment,
            created_by=sender_detailed_user,
            modified_by=sender_detailed_user,
            content=request_data.get("content")
        )