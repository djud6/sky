from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_issue_category import AssetIssueCategory
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class IssueCategoryHelper():

    @staticmethod
    def get_all_categories(db_name):
        return AssetIssueCategory.objects.using(db_name).all()