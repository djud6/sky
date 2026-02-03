from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_request_justification import AssetRequestJustificationModel
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetRequestJustificationHelper():

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_all_justifications(db_name):
        return AssetRequestJustificationModel.objects.using(db_name).all()

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_justification_by_id(justification_id, db_name):
        try:
            return AssetRequestJustificationModel.objects.using(db_name).get(justification_id=justification_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.JDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.JDNE_0, e), status=status.HTTP_400_BAD_REQUEST)   

    # --------------------------------------------------------------------------------------

