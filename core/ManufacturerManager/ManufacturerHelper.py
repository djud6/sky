from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_manufacturer import AssetManufacturerModel
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ManufacturerHelper():

    @staticmethod
    def get_manufacturer_by_asset_type(asset_id, db_name):
        try:
            return AssetManufacturerModel.objects.using(db_name).filter(asset_type__id=asset_id), Response(status=status.HTTP_302_FOUND)
        except AssetManufacturerModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MDNE_0))
            return None, Response(CustomError.get_full_error_json(CustomError.MDNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def get_manufacturer_id_by_name(manufacturer_name, db_name):
        return AssetManufacturerModel.objects.using(db_name).filter(name=manufacturer_name).values_list('id', flat=True)[0]

    @staticmethod
    def get_manufacturer_by_name(manufacturer_name, db_name):
        try:
            return AssetManufacturerModel.objects.using(db_name).get(name=manufacturer_name), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MNDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.MNDNE_0, e), status=status.HTTP_400_BAD_REQUEST)
            
    @staticmethod
    def manufacturer_exists(manufacturer_name, db_name):
        return AssetManufacturerModel.objects.using(db_name).filter(name=manufacturer_name).exists()