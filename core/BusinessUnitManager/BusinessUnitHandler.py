from rest_framework.response import Response
from rest_framework import status
from .BusinessUnitHelper import BusinessUnitHelper
from .BusinessUnitUpdater import BusinessUnitUpdater
from api.Serializers.serializers import BusinessUnitSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class BusinessUnitHandler():
    
    @staticmethod
    def handle_get_business_units(user):
        try:
            queryset = BusinessUnitHelper.get_all_business_units(user.db_access)
            serializer = BusinessUnitSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_business_units_for_user(user):
        try:
            queryset = BusinessUnitHelper.get_all_business_units(user.db_access)
            relevant_qs = BusinessUnitHelper.filter_business_units_for_user(queryset, user).order_by('name')
            serializer = BusinessUnitSerializer(relevant_qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
