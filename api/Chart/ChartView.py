from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.ChartCalculations.ChartCalculations import ChartCalculations
from api_auth.Auth_DB.DBMethods import DBMethods
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


# This class returns number of assets that are active, in repair, maintenance, and accident.
class GetAssetStatusBreakdown(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_asset_status_breakdown(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetAssetProcessBreakdown(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_asset_process_breakdown(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetAssetsAndOperatorsCountPerLocation(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_assets_and_operators_count_per_location(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetAssetPerformanceLeaderboard(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_asset_performance_leaderboard(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetLocationAssetTypes(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_location_asset_types(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetLocationMaintenanceDowntimeAverage(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_location_maintenance_downtime_average(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# This class returns parameters for the assets chart
class GetAssetChartParams(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response({"airports":11, "tac":32, "tech_ops":12, "flight_ops":5}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# This class returns parameters for the accident chart
class GetAccidentChartParams(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response({"airports":21, "tac":23, "tech_ops":5, "flight_ops":55}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# This class returns parameters for the maintenance chart
class GetMaintenanceChartParams(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response({"airports":4, "tac":23, "tech_ops":1, "flight_ops":3}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
            

# This class returns parameters for the repairs chart
class GetRepairsChartParams(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response({"airports":33, "tac":11, "tech_ops":19, "flight_ops":9}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetFuelUsageVolume(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_fleet_usage_volume(request.user), status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)    


class GetFleetUsage(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_fleet_usage(request.user), status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetFuelUsage(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, _unit):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            if(_unit == "dollar"):
                return Response(ChartCalculations.get_fuel_usage_dollar(), status=status.HTTP_200_OK)
            elif(_unit == "volume"):
                return Response(ChartCalculations.get_fuel_usage_volume(), status=status.HTTP_200_OK)
            else:
                return Response(CustomError.get_full_error_json(CustomError.UP_0), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetLifeCycleCount(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_asset_lifecycle_count(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetLifeCycleCountPerType(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_asset_lifecycle_count_by_type(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetOperationalCost(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_operational_cost(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetFuelCost(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, _time_unit):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_fuel_cost(request.user, _time_unit.lower()), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetdailyChecksAndAssets(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.get_daily_checks_and_assets(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class GetProcessCostByLocation(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.process_cost_by_location(request.user), status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
class GetWorkOrderCompletionTime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(ChartCalculations.work_order_completion_time(request.user))
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

class GetFleetUtilizationDatetime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return Response(ChartCalculations.get_fleet_usage_datetime(request.user, start_date, end_date), status=status.HTTP_200_OK)
    
class GetFleetUtilizationPercentageDatetime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return Response(ChartCalculations.get_fleet_usage_percent(request.user, start_date, end_date), status=status.HTTP_200_OK)
