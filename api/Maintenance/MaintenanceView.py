from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.MaintenanceManager.MaintenanceHandler import MaintenanceHandler
from core.MaintenanceForecastManager.MaintenanceForecastHandler import MaintenanceForecastHandler
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
from core.Helper import HelperMethods

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AddBatchMaintenanceRequest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        data = HelperMethods.json_str_to_dict(request.POST['data'])
        files = request.FILES.getlist('files')
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_add_batch_maintenance_request(data, files, request.user)


class UpdateMaintenanceStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_update_maintenance_status(request.data, request.user)


class ListMaintenance(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_list_maintenance(request.user)


class ListCompletedMaintenance(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_list_completed_maintenance(request.user)


class GetMaintenanceByVIN(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, _vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_get_maintenance_by_vin(_vin, request.user)


class GetMaintenanceDetailsByID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, maintenance_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_get_maintenance_details_by_id(maintenance_id, request.user)


class GetMaintenanceDetailsByWorkOrder(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, work_order):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_get_maintenance_details_by_work_order(work_order, request.user)


class ListInspections(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_list_inspections(request.user)


class UpdateVendorAndEstimatedDeliveryDate(APIView):
    authentiation_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def patch(self, request, maintenance_id=None):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_update_vendor_and_estimated_delivery_date(maintenance_id, request.data, request.user)


# Returns the number of incomplete maintenance requests
class GetIncompleteMaintenanceRequestCount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_get_incomplete_maintenance_request_count(request.user)


# Returns the number of complete maintenance requests
class GetCompleteMaintenanceRequestCount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_get_complete_maintenance_request_count(request.user)


# Returns the percentage of complete maintenance requests
class GetMaintenanceRequestPercentageComplete(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_get_maintenance_request_percentage_complete(request.user)


# Adds maintenance forecast rule to the table
class AddMaintenanceForecastRule(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceForecastHandler.handle_add_maintenance_forecast_rule(request.data, request.user)


# Returns all maintenance forecast rules in the database
class GetMaintenanceForecastRules(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceForecastHandler.handle_get_maintenance_forecast_rules(request.user)


# Returns all maintenance forecast rules for a given VIN
class GetMaintenanceForecastRulesByVIN(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, _vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceForecastHandler.handle_get_maintenance_forecast_rules_by_vin(_vin, request.user)


class GetMaintenanceForecastRuleDetailByID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, maintenance_rule_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceForecastHandler.handle_get_maintenance_forecast_rule_details_by_id(maintenance_rule_id, request.user)


class GetMaintenanceForecastRuleDetailByCustomID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, custom_maintenance_rule_id):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceForecastHandler.handle_get_maintenance_forecast_rule_details_by_custom_id(custom_maintenance_rule_id, request.user)


class GetMaintenanceForecastForRule(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceForecastHandler.handle_get_maintenance_forecast_for_rule(request.data, request.user)


class UpdateMaintenance(APIView):        
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return MaintenanceHandler.handle_update_maintenance(request.data, request.user)

# add supporting files
class AddMaintenanceFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, maintenance_id):
        
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        
        file_specs = HelperMethods.json_str_to_dict(request.POST['file_specs'])
        

        return MaintenanceHandler.handle_add_supporting_files(maintenance_id, file_specs, request.FILES.getlist('files'), request.user)