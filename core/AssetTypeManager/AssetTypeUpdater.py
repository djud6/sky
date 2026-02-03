from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_type import AssetTypeModel
from ..AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
from ..UserManager.UserHelper import UserHelper
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeUpdater():

    @staticmethod
    def create_asset_type_entry(asset_type_data, user):
        try:
            db_name = user.db_access
            asset_type_checks = AssetTypeChecksHelper.get_checks_by_asset_type(asset_type_data.get("asset_type").strip(), db_name)
            asset_type_entry = AssetTypeModel(name=asset_type_data.get("asset_type").strip(), asset_type_checks=asset_type_checks)
            return AssetTypeUpdater.update_asset_type_created_by(asset_type_entry, user)
        except Exception as e:
            Logger.getLogger().error(CustomError.ATCF_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.ATCF_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def update_asset_type_created_by(asset_type_entry_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            asset_type_entry_obj.created_by = detailed_user
            asset_type_entry_obj.modified_by = detailed_user
            return asset_type_entry_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_14, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_14, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def update_asset_type_checks_fk(asset_type_obj, checks_obj):
        asset_type_obj.asset_type_checks = checks_obj
        updated_asset_type_obj = asset_type_obj.save()
        return updated_asset_type_obj