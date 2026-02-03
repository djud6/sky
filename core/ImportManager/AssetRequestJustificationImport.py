from rest_framework.response import Response
from rest_framework import status
from ..AssetRequestJustificationManager.AssetRequestJustificationUpdater import AssetRequestJustificationUpdater
from api.Models.asset_request_justification import AssetRequestJustificationModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetRequestJustificationImport():

    @staticmethod
    def import_asset_request_justification_csv(parsed_data, db_name):
        try:
            asset_request_justification_entries = []
            for asset_request_justification_row in parsed_data:
                if not AssetRequestJustificationModel.objects.using(db_name).filter(name=asset_request_justification_row.get("name")).exists():
                    entry = AssetRequestJustificationUpdater.create_asset_request_justification_entry(asset_request_justification_row)
                    asset_request_justification_entries.append(entry)
            AssetRequestJustificationModel.objects.using(db_name).bulk_create(asset_request_justification_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_9, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_9, e), status=status.HTTP_400_BAD_REQUEST)