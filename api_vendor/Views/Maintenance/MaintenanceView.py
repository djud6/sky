from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api_vendor.Auth.AuthHelper import AuthHelper
from core.MaintenanceManager.MaintenanceHandler import MaintenanceHandler
from core.CostManager.CostHandler import LaborHandler, PartsHandler
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from core.Helper import HelperMethods
from types import SimpleNamespace

from GSE_Backend.errors.ErrorDictionary import CustomError
import logging


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


# OUTBOUND -----------------------------------------------------------------------------------

"""
    APIs that send out requests to the vendor system go here.
"""

# INBOUND ------------------------------------------------------------------------------------

"""
    APIs that process requests internally go here.
"""


class GetMaintenanceRequests(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return MaintenanceHandler.handle_get_maintenance_for_vendor(request.data)


class GetMaintenanceRequestDetails(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return MaintenanceHandler.handle_get_maintenance_details_for_vendor(request.data)


class UpdateMaintenanceStatus(APIView):
    permission_classes = [AllowAny]

    def post(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = HelperMethods.json_str_to_dict(request.POST["data"])
            status_data = data.get("status_data")
            labor_costs = data.get("labor_costs")
            parts_costs = data.get("parts_costs")

            client_name = status_data.get("client_name")
            auth_company, resp = VendorOpsHelper.get_auth_db_company_by_name(client_name)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
                
            db_name = auth_company.company_db_access

            maintenance_id = status_data.get("maintenance_id")
            file_specs = HelperMethods.json_str_to_dict(request.POST["file_specs"])
            request_files = request.FILES.getlist("files")
            user = SimpleNamespace(
                            db_access=db_name,
                            email=None
                        )
                        
            # Update status
            status_update_response = MaintenanceHandler.handle_update_maintenance_status(
                status_data, None, db_name
            )
            if status_update_response.status_code != status.HTTP_202_ACCEPTED:
                return status_update_response

            # Add costs
            if len(labor_costs) > 0:
                labor_response = LaborHandler.handle_add_batch_labor_costs(labor_costs, user)
                if labor_response.status_code != status.HTTP_201_CREATED:
                    return labor_response
            
            if len(parts_costs) > 0:
                parts_response = PartsHandler.handle_add_batch_parts_costs(parts_costs, user)
                if parts_response.status_code != status.HTTP_201_CREATED:
                    return parts_response

            # Upload files
            if len(request_files) > 0 :
                file_upload_response = MaintenanceHandler.handle_add_supporting_files(
                    maintenance_id,
                    file_specs,
                    request_files,
                    user    
                )
                if file_upload_response.status_code != status.HTTP_200_OK:
                    return file_upload_response

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


class UploadMaintenancesFiles(APIView):
    permission_classes = [AllowAny]

    def post(self, request, client_name):
        if not AuthHelper.authenticate_vendor_request(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = HelperMethods.json_str_to_dict(request.POST["data"])

            client_name = data.get("client_name")
            auth_company, resp = VendorOpsHelper.get_auth_db_company_by_name(client_name)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
                
            db_name = auth_company.company_db_access

            maintenance_id = data.get("maintenance_id")
            file_specs = HelperMethods.json_str_to_dict(request.POST["file_specs"])
            request_files = request.FILES.getlist("files")
            user = SimpleNamespace(
                            db_access=db_name,
                            email=None
                        )

            return MaintenanceHandler.handle_add_supporting_files(
                maintenance_id,
                file_specs,
                request_files,
                user    
            )

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

