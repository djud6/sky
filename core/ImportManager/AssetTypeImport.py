from rest_framework.response import Response
from rest_framework import status
from ..AssetTypeManager.AssetTypeUpdater import AssetTypeUpdater
from api.Models.asset_type import AssetTypeModel
from api.Models.asset_type_checks import AssetTypeChecks
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeImport():

    @staticmethod
    def import_asset_type_csv(parsed_data, user):
        try:
            db_name = user.db_access
            asset_type_entries = []
            for asset_type_row in parsed_data:
                if not AssetTypeModel.objects.using(db_name).filter(name=asset_type_row.get("name")).exists():
                    entry, entry_response = AssetTypeUpdater.create_asset_type_entry(asset_type_row, user)
                    if entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return entry_response
                    asset_type_entries.append(entry)
            AssetTypeModel.objects.using(db_name).bulk_create(asset_type_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_4, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_4, e), status=status.HTTP_400_BAD_REQUEST)