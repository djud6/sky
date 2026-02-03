from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_request_justification import AssetRequestJustificationModel
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetRequestJustificationUpdater():

    @staticmethod
    def create_asset_request_justification_entry(asset_request_justification_data):
        return AssetRequestJustificationModel(
            name=asset_request_justification_data.get("name")
        )