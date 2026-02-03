from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_issue_category import AssetIssueCategory
from .IssueCategoryHelper import IssueCategoryHelper
from api.Serializers.serializers import AssetIssueCategorySerializer
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class IssueCategoryHandler():

    @staticmethod
    def handle_get_all_categories(user):
        try:
            all_categories = IssueCategoryHelper.get_all_categories(user.db_access)
            ser = AssetIssueCategorySerializer(all_categories, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)