from rest_framework.response import Response
from rest_framework import status
from .FleetGuruHelper import FleetGuruHelper
from .FleetGuruUpdater import FleetGuruUpdater
from api.Serializers.serializers import FleetGuruSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class FleetGuruHandler():
    
    @staticmethod
    def handle_get_information(_process_name, user):
        process_list = ["repairs", "maintenance", "asset_request", "incidents", "asset_removal", "issues", "fuel_orders", "fuel_tracking", "operators", "fleet_at_a_glance", "asset_transfer"]
        _process_name = _process_name.lower()
        
        if any(_process_name in s for s in process_list):
            qs = FleetGuruHelper.get_fleet_guru_process(_process_name, user.db_access)
            ser = FleetGuruSerializer(qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.FG_DNE))
            return Response(CustomError.get_full_error_json(CustomError.FG_DNE), status=status.HTTP_400_BAD_REQUEST)