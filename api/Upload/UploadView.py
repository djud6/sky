from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_csv.parsers import CSVParser
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from core.ImportManager.AssetImport import AssetImport
from core.ImportManager.LocationImport import LocationImport
from core.ImportManager.AssetTypeImport import AssetTypeImport
from core.ImportManager.AssetTypeChecksImport import AssetTypeChecksImport
from core.ImportManager.FuelTypeImport import FuelTypeImport
from core.ImportManager.RolePermissionsImport import RolePermissionsImport
from core.ImportManager.BusinessUnitImport import BusinessUnitImport
from core.ImportManager.JobSpecificationImport import JobSpecificationImport
from core.ImportManager.ManufacturerImport import ManufacturerImport
from core.ImportManager.EquipmentTypeImport import EquipmentTypeImport
from core.ImportManager.CompanyImport import CompanyImport
from core.ImportManager.AssetRequestJustificationImport import AssetRequestJustificationImport
from core.ImportManager.InspectionTypeImport import InspectionTypeImport
from core.ImportManager.ApprovedVendorImport import ApprovedVendorImport
from core.ImportManager.UserImport import UserImport
from core.ImportManager.CurrencyImport import CurrencyImport
from core.ImportManager.MaintenanceRuleImport import MaintenanceRuleImport
from core.ImportManager.MaintenanceImport import MaintenanceImport
from django.http import HttpResponse
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class UploadCurrencyCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request, db_access):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "currency_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = CurrencyImport.import_currency_csv(parsed_data, db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadCompanyCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request, db_access):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "company_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = CompanyImport.import_company_csv(parsed_data, db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadRolePermissionsCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request, db_access):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "role_permissions_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = RolePermissionsImport.import_role_permissions_csv(parsed_data, db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadAssetCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "asset_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = AssetImport.import_asset_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)

            '''if(upload_success):
                if(zip_file is not None):
                    response = HttpResponse(zip_file.getvalue(), content_type='application/zip', status=status.HTTP_406_NOT_ACCEPTABLE)
                    response['Content-Disposition'] = 'attachment; filename="' + zip_file.name
                    return response
                else:
                    return HttpResponse(status=status.HTTP_200_OK)'''


class UploadLocationCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "location_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = LocationImport.import_location_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadAssetTypeCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "asset_type_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = AssetTypeImport.import_asset_type_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadAssetTypeChecksCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "asset_type_checks_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = AssetTypeChecksImport.import_asset_type_checks_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadFuelTypeCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "fuel_type_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = FuelTypeImport.import_fuel_type_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadBusinessUnitCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "business_unit_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = BusinessUnitImport.import_business_unit_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadJobSpecificationCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "job_specification_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = JobSpecificationImport.import_job_specification_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadManufacturerCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "manufacturer_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = ManufacturerImport.import_manufacturer_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadManufacturerAssetTypeCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "manufacturer_asset_type_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = ManufacturerImport.import_manufacturer_asset_type_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadEquipmentTypeCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "equipment_type_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = EquipmentTypeImport.import_equipment_type_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadAssetRequestJustificationCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "asset_request_justification_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = AssetRequestJustificationImport.import_asset_request_justification_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadInspectionTypeCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "inspection_type_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = InspectionTypeImport.import_inspection_type_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)
                

class UploadApprovedVendorTaskCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "approved_vendor_task_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = ApprovedVendorImport.import_approved_vendor_task_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadApprovedVendorDepartmentCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "approved_vendor_department_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = ApprovedVendorImport.import_approved_vendor_department_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadApprovedVendorCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "approved_vendor_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = ApprovedVendorImport.import_approved_vendor_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadUserCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "user_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = UserImport.import_user_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadUserLocationCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "user_location_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = UserImport.import_user_location_csv(parsed_data, request.user.db_access)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadMaintenanceRuleCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "maintenance_rule_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = MaintenanceRuleImport.import_maintenance_rule_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)


class UploadMaintenanceCSV(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FormParser, MultiPartParser, CSVParser]

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            expected_file_name = "maintenance_template.csv"
            csvParse = CSVParser()
            data = request.FILES.get('csv_file')
            if str(data) == expected_file_name:
                parsed_data = csvParse.parse(stream=data)
                upload_response = MaintenanceImport.import_maintenance_csv(parsed_data, request.user)
                return upload_response
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UFN_0, "Expected " + expected_file_name))
                return Response(CustomError.get_full_error_json(CustomError.UFN_0, "Expected " + expected_file_name), status=status.HTTP_400_BAD_REQUEST)