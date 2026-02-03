from rest_framework.response import Response
from rest_framework import status
from ..AssetTypeChecksManager.AssetTypeChecksUpdater import AssetTypeChecksUpdater
from api.Models.asset_type_checks import AssetTypeChecks
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeChecksImport():

    @staticmethod
    def import_asset_type_checks_csv(parsed_data, db_name):
        try:
            asset_type_checks_entries = []
            asset_type_names = []
            for asset_type_checks_row in parsed_data:
                asset_type_name = asset_type_checks_row.get("asset_type").strip()
                if asset_type_name not in asset_type_names and not AssetTypeChecks.objects.using(db_name).filter(asset_type_name=asset_type_checks_row.get("asset_type")).exists():
                    entry = AssetTypeChecksUpdater.create_asset_type_checks_entry(asset_type_checks_row)
                    asset_type_checks_entries.append(entry)
                    asset_type_names.append(asset_type_name)

            AssetTypeChecks.objects.using(db_name).bulk_create(asset_type_checks_entries)
            
            
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_4, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_4, e), status=status.HTTP_400_BAD_REQUEST)