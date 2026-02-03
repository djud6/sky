from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django import forms
from core.AssetManager.AssetHandler import AssetHandler
from core.Helper import HelperMethods
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
from core.AccidentManager.AccidentHandler import AccidentHandler

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class UploadCSVForm(forms.Form):
    title = forms.CharField(required=False, max_length=50)
    path = forms.CharField(required=False)
    csv_file = forms.FileField()

# Add asset
class AddAsset(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_asset(request.data, request.user)

# Add bulk asset
class AddBulkAsset(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_bulk_asset(request.data, request.user)

# methods containing the CRUD requests
class SearchByFullVINView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, pk):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_search_by_full_vin_or_unit_number(pk, request.user)

# returns a queryset of asset objects that have the last 6 digits of a vin number
class SearchByVINAndUnitNumber(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, substring):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_search_asset_by_VIN_and_Unit_Number(substring, request.user)
    
# this class returns all asset vins
class GetAllAssetVINs(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_all_asset_vins(request.user)


# this returns all assets
class GetAllAssets(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_all_assets(request.user)

# return average maintanence cost for the fleet
class GetAverageMaintenanceCost(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        return AssetHandler.handle_get_average_maintenance_cost(request.user)

# return a list of assets which have end of life in 1 year or less
class GetUpcommingEndOfLife(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_upcomming_end_of_life(request.user)

# add warranty files
class AddWarrantyFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_warranty_files(request, vin)

# add insurance files
class AddInsuranceFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_insurance_files(request, vin)


# add registration files
class AddRegistrationFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_registration_files(request, vin)
    
# add other files
class AddOtherFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_other_files(request, vin)



# add supporting files
class AddSupportingFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_supporting_files(vin, HelperMethods.json_str_to_dict(request.POST['file_specs']), request.FILES.getlist('files'), request.user)


# get latest registration and insurance files and all warranty files
class GetAssetFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_asset_files(vin, request.user)

class GetAllInsAndRegFiles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_all_ins_and_reg_files(vin, request.user)


# get preventable/non-preventable downtime for asset
class GetAssetDowntime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AccidentHandler.handle_get_accident_downtime_for_asset(vin, request.user)

# Get the downtime for the date range for a vin
class GetAssetDowntimeDaterange(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(
                CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AccidentHandler.handle_get_asset_downtime_date_range(start_date, end_date, request.user)

# get preventable/non-preventable downtime for fleet
class GetFleetDowntime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AccidentHandler.handle_get_accident_downtime_for_fleet(request.user)


# Is the mileage and/or hours inputed for asset valid
class IsUsageValid(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_is_usage_valid(request.data, request.user)


# Get the types of checks that are required to be done by operators for this asset
class GetAssetChecks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_asset_checks(vin, request.user)


# Return all job specifications
class ListJobSpecification(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_list_job_specification(request.user)

# Get Maintenance Cost per distance unit (mile/km/hour)
class GetAverageMaintenanceCostPerUnit(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_average_maintenance_cost_per_mileage(start_date, end_date, request.user)


class GetAverageCostPerUnit(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_average_cost_per_unit(start_date, end_date, request.user)


# Return all the different types of usage tracking for assets
class GetUsageTrackingTypes(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_usage_tracking_types()


class UpdateAsset(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_update_asset(request.data, request.user)
    
class UpdateAssetCustomFilter(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_update_asset_custom_fields(request.data, vin, request.user)
        
class DeleteAssetCustomFilter(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_delete_asset_custom_fields(request.data, vin, request.user)

class ReassignAsset(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_reassign_asset(request.data, request.user)


class SetAssetParent(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_set_asset_parent(request.data, request.user)


class AddAssetChildren(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_asset_children(request.data, request.user)


class RemoveAssetParent(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_remove_asset_parent(request.data, request.user)


class RemoveAssetChildren(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_remove_asset_children(request.data, request.user)


class GetAssetChildren(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_asset_children(vin, request.user)


class SetAssetStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_set_asset_status(request.data, request.user)
    
class GetMeanTimeBetweenFailure(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_mean_time_between_failure(request.user, start_date, end_date)


class PostAnnualReport(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_add_annual_report(request, vin)



class GetAnnualReport(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_annual_report(vin, request.user)

class GetAnnualReportKPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, year):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_annual_report_kpi(year, request.user)

# class GetAssetFiles(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, vin):
#         if auth_token_check(request.user):
#             Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
#             return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
#         return AssetHandler.handle_get_asset_files(vin, request.user)


class GetLifeCycleDisposalScheduleKPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return AssetHandler.handle_get_lifecycle_disposal_schedule_kpi(request.user)
