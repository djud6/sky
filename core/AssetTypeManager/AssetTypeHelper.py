from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_type import AssetTypeModel
from api.Models.asset_type_checks import AssetTypeChecks
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeHelper():

    @staticmethod
    def get_all_asset_types(db_name):
        return AssetTypeModel.objects.using(db_name).all()

    @staticmethod
    def get_asset_type_id_by_name(asset_type_name, db_name):
        return AssetTypeModel.objects.using(db_name).filter(name=asset_type_name).values_list('id', flat=True)[0]

    @staticmethod
    def get_asset_type_by_name(asset_type_name, db_name):
        try:
            return AssetTypeModel.objects.using(db_name).get(name=asset_type_name), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ATNDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ATNDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_asset_types_with_checks(db_name):
        asset_type_names_with_checks = list(AssetTypeChecks.objects.using(db_name).all().values_list('asset_type_name', flat=True))
        return AssetTypeModel.objects.using(db_name).filter(name__in=asset_type_names_with_checks)

    @staticmethod
    def get_asset_types_without_checks(db_name):
        asset_type_names_with_checks = list(AssetTypeChecks.objects.using(db_name).all().values_list('asset_type_name', flat=True))
        return AssetTypeModel.objects.using(db_name).all().exclude(name__in=asset_type_names_with_checks)

    @staticmethod
    def asset_type_exists_by_name(asset_type_name, db_name):
        return AssetTypeModel.objects.using(db_name).filter(name=asset_type_name).exists()

    @staticmethod
    def asset_type_exists_by_id(asset_type_id, db_name):
        return AssetTypeModel.objects.using(db_name).filter(id=asset_type_id).exists()