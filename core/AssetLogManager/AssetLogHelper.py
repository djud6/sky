from rest_framework.response import Response
from rest_framework import status
from ..UserManager.UserHelper import UserHelper
from api.Models.asset_log import AssetLog
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetLogHelper():

    @staticmethod
    def select_related_to_asset_log(queryset):
        return queryset.select_related('created_by', 'modified_by', 'location')
    
    @staticmethod
    def get_logs_by_vin(VIN, db_name):
        return AssetLog.objects.using(db_name).select_related('created_by', 'modified_by').filter(VIN=VIN)

    @staticmethod
    def get_logs_by_vin_for_daterange(VIN, start_date, end_date, db_name):
        return AssetLog.objects.using(db_name).select_related('created_by', 'modified_by').filter(VIN=VIN, asset_log_created__range=[start_date, end_date])

    @staticmethod
    def get_logs_for_daterange(start_date, end_date, db_name):
        return AssetLog.objects.using(db_name).filter(asset_log_created__range=[start_date, end_date])