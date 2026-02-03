from rest_framework.views import APIView
import os
from core.WebJobManager.WebJobHandler import WebJobHandler
import logging
from rest_framework.permissions import AllowAny
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceAndRepairSetAssetInop(APIView):
    permission_classes = (AllowAny,)
    def put(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST) 

            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_maintenance_and_repair_set_asset_inop()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class CreateFleetDailySnapshot(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST) 

            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_create_fleet_daily_snapshot()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class CreateCostDailySnapshot(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST) 

            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_create_cost_daily_snapshot()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
            


class CreateDailyCountsSnapshot(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST) 

            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_create_daily_counts_snapshot()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# Notifies managers about maintenance due today
# Designed to run once a day
class NotifyMaintenance(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST) 
            print(request.data.get('key')) 
            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_notify_maintenance()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class CreateDailyCurrencySnapshot(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST) 

            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_create_daily_currency_snapshot()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# Notifies users about any upcoming expiry dates
# Designed to run once a week
class NotifyExpiry(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST) 

            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_notify_expiry()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# For hitting service bus
class ReceiveMessages(APIView):
    permission_classes = (AllowAny, )
    def post(self, request):
        try:
            webjob_key = os.getenv('WebJobKey')
            if webjob_key is None:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MEV_0))
                return Response(CustomError.get_full_error_json(CustomError.MEV_0), status=status.HTTP_400_BAD_REQUEST)

            if webjob_key == request.data.get('key'):
                return WebJobHandler.handle_receive_messages()

            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
