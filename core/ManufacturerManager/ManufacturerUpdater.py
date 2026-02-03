from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_manufacturer import AssetManufacturerModel
from ..UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ManufacturerUpdater():

    @staticmethod
    def create_manufacturer_entry(manufacturer_data, user):
        try:
            asset_manufacturer_entry = AssetManufacturerModel(name=manufacturer_data.get("manufacturer").strip())
            return ManufacturerUpdater.update_manufacturer_created_by(asset_manufacturer_entry, user)
        except Exception as e:
            Logger.getLogger().error(CustomError.AMCF_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.AMCF_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_manufacturer_asset_type_entry(manufacturer_asset_type_data):
        return AssetManufacturerModel.asset_type.through(
            assetmanufacturermodel_id=manufacturer_asset_type_data.get("manufacturer"),
            assettypemodel_id=manufacturer_asset_type_data.get("asset_type")
        )

    @staticmethod
    def update_manufacturer_created_by(asset_manufacturer_entry_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            asset_manufacturer_entry_obj.created_by = detailed_user
            asset_manufacturer_entry_obj.modified_by = detailed_user
            return asset_manufacturer_entry_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_15, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_15, e), status=status.HTTP_400_BAD_REQUEST)