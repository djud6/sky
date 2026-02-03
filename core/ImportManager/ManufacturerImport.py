from rest_framework.response import Response
from rest_framework import status
from ..ManufacturerManager.ManufacturerUpdater import ManufacturerUpdater
from ..ManufacturerManager.ManufacturerHelper import ManufacturerHelper
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from api.Models.asset_manufacturer import AssetManufacturerModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ManufacturerImport():

    @staticmethod
    def import_manufacturer_csv(parsed_data, user):
        try:
            manufacturer_entries = []
            for manufacturer_row in parsed_data:
                if not AssetManufacturerModel.objects.using(user.db_access).filter(name=manufacturer_row.get("name")).exists():
                    entry, entry_response = ManufacturerUpdater.create_manufacturer_entry(manufacturer_row, user)
                    if entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return entry_response
                    manufacturer_entries.append(entry)
            AssetManufacturerModel.objects.using(user.db_access).bulk_create(manufacturer_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_3, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_3, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def import_manufacturer_asset_type_csv(parsed_data, db_name):
        try:
            manufacturer_asset_type_entries = []
            for manufacturer_asset_type_row in parsed_data:
                manufacturer_asset_type_row['manufacturer'] = ManufacturerHelper.get_manufacturer_id_by_name(manufacturer_asset_type_row.get("manufacturer").strip(), db_name)
                manufacturer_asset_type_row['asset_type'] = AssetTypeHelper.get_asset_type_id_by_name(manufacturer_asset_type_row.get("asset_type").strip(), db_name)
                if not AssetManufacturerModel.asset_type.through.objects.using(db_name).filter(assetmanufacturermodel_id=manufacturer_asset_type_row.get("manufacturer")).filter(assettypemodel_id=manufacturer_asset_type_row.get("asset_type")).exists():
                    entry = ManufacturerUpdater.create_manufacturer_asset_type_entry(manufacturer_asset_type_row)
                    manufacturer_asset_type_entries.append(entry)
            AssetManufacturerModel.asset_type.through.objects.using(db_name).bulk_create(manufacturer_asset_type_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_8, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_8, e), status=status.HTTP_400_BAD_REQUEST)


    