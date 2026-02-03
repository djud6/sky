from rest_framework.response import Response
from rest_framework import status
from .LocationHelper import LocationHelper
from .LocationUpdater import LocationUpdater
from api.Serializers.serializers import LocationSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class LocationHandler():
    
    @staticmethod
    def handle_list_locations(user):
        try:
            queryset = LocationHelper.get_all_locations(user.db_access).order_by('location_code')
            ser = LocationSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_list_locations_for_user(user):
        try:
            queryset = LocationHelper.get_all_locations_for_user(user).order_by('location_code')
            ser = LocationSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)