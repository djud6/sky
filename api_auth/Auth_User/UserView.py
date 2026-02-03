from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.UserManager.UserHelper import UserHelper
from core.UserManager.UserHandler import UserHandler
from core.UserManager.UserFileActions import UserFileActions
from ..Serializers.serializers import LinkedUserModelSerializer, DetailedUserSerializer, UserConfigurationSerializer
from api.Serializers.serializers import AccidentSerializer
from core.FileManager.FileHelper import FileHelper
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from core.HistoryManager.UserHistory import UserHistory
from core.HistoryManager.DetailedUserHistory import DetailedUserHistory
from core.Helper import HelperMethods
from core.FileManager.ImageManager import ImageManager
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from api.Models.accident_report import AccidentModel
from api.Models.Cost.acquisition_cost import AcquisitionCost
from api.Models.approval import Approval
from api.Models.asset_daily_checks import AssetDailyChecksModel
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_file import AssetFile
from api.Models.asset_issue_category import AssetIssueCategory
from api.Models.asset_disposal_file import AssetDisposalFile
from api.Models.asset_issue import AssetIssueModel
from api.Models.asset_log import AssetLog
from api.Models.asset_manufacturer import AssetManufacturerModel
from api.Models.asset_model import AssetModel
from api.Models.asset_request import AssetRequestModel
from api.Models.asset_transfer import AssetTransfer
from api.Models.asset_type_checks import AssetTypeChecks
from api.Models.asset_type import AssetTypeModel
from api.Models.Cost.delivery_cost import DeliveryCost
from api.Models.equipment_type import EquipmentTypeModel
from api.Models.error_report import ErrorReport
from api.Models.Cost.fuel_cost import FuelCost
from api.Models.fuel_type import FuelType
from api.Models.Cost.insurance_cost import InsuranceCost
from api.Models.Cost.labor_cost import LaborCost
from api.Models.Cost.license_cost import LicenseCost
from api.Models.maintenance_forecast import MaintenanceForecastRules
from api.Models.maintenance_request_file import MaintenanceRequestFile
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.Cost.parts import Parts
from api.Models.Cost.rental_cost import RentalCost
from api.Models.repair_file import RepairFile
from api.Models.repairs import RepairsModel
from api.Models.transfer_file import TransferFile
from api.Models.dailyinspectionmodel import DailyInspection
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


# Get all users
class GetAllUsers(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        return UserHandler.handle_get_all_users(request.user)
    

# Get all role permissions
class GetAllRolePermissions(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        return UserHandler.handle_get_all_role_permissions(request.user)
    

class GetAllUsers(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        return UserHandler.handle_get_all_users(request.user)

# Get initial users
class GetInitialUserData(APIView):
    """
    Separate endpoint to get user data after successful authentication
    This replaces sending all data during login
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = request.user
            user_ser = LinkedUserModelSerializer(UserHelper.get_user(user.id))
            detailed_user_info = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            detailed_user_ser = DetailedUserSerializer(detailed_user_info)
            user_config = UserHelper.get_user_config_by_user_id(
                detailed_user_info.detailed_user_id, user.db_access
            )
            user_config_serializer = UserConfigurationSerializer(user_config)
            
            session_info = {
                'user': user_ser.data,
                'detailed_user': detailed_user_ser.data,
                'user_config': user_config_serializer.data,
            }
            
            # Get auxiliary data only when needed, not during login
            aux_info, aux_info_response = CustomAuthToken.aux_data(user)
            if aux_info_response.status_code != status.HTTP_200_OK:
                return aux_info_response
            
            full_user_info = {**session_info, **aux_info}
            
            return Response(full_user_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), 
                           status=status.HTTP_400_BAD_REQUEST)

    

# Create new user
class CreateUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        create_user_response = UserHandler.handle_create_user(request.data, request.user)
        if create_user_response.status_code != status.HTTP_201_CREATED:
            return create_user_response
            
        return UserHandler.handle_add_user_locations(request.data, request.user)


# Edit user account
class EditUserAccount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_edit_user_account(request.data, request.user)


# Edit user account - only superusers are allowed
class EditAnyUserAccount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_edit_any_user_account(request.data, request.user)


# Change user password
class UpdateUserPassword(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_update_user_password(request.data, request.user)

# accepts emailid in request body and sends an a link to provided email 
class ForgotPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        return UserHandler.handle_forgot_password(self, request)

# checks the token when user clicks the link
class PasswordTokenCheck(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        return UserHandler.handle_forgot_password_token_check(self, request, uidb64, token)

# generates and sends the password when user confirms
class ForgotPasswordGenerate(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        return UserHandler.handle_forgot_password_generate(self, request)

# Get user info based on id of current authenticated user
class GetUserInformation(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            user_Info = UserHelper.get_user(request.user.id)
            detailed_user_info = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            user_config = UserHelper.get_user_config_by_user_id(detailed_user_info.detailed_user_id, request.user.db_access)

            if not user_Info == status.HTTP_404_NOT_FOUND:
                user_serializer = LinkedUserModelSerializer(user_Info)
                detailed_user_serializer = DetailedUserSerializer(detailed_user_info)
                user_config_serializer = UserConfigurationSerializer(user_config)
                return Response({"user": user_serializer.data,
                "detailed_user": detailed_user_serializer.data,
                "user_config": user_config_serializer.data},
                status=status.HTTP_200_OK)

            Logger.getLogger().error(CustomError.UDNE_0)
            return Response(CustomError.get_full_error_json(CustomError.UDNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


#Get All User Actions
#TODO: add another column to the return response
class GetUserActions(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            detailed_user_info = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            
            if not detailed_user_info == status.HTTP_404_NOT_FOUND:
                detailed_user_serializer = DetailedUserSerializer(detailed_user_info)
                user_id = detailed_user_serializer.data['detailed_user_id']

                # Filter AccidentModel instances based on created_by or modified_by user ID
                accidents = AccidentModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                accident_data = [accident['accident_id'] for accident in accidents.values('accident_id')]

                # Filter AcquisitionCost Model instances based on created_by or modified_by user ID 
                acquisition_costs = AcquisitionCost.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                acquisition_cost_data = [cost['id'] for cost in acquisition_costs.values('id')]

                # Filter ApprovalModel instances based on approving_user_id or requesting_user_id
                approvals = Approval.objects.filter(Q(approving_user_id=user_id) | Q(requesting_user_id=user_id))
                approval_data = [approval['approval_id'] for approval in approvals.values('approval_id')]

                # Filter AssetDailyChecksModel instances based on modified_by user ID
                daily_checks = AssetDailyChecksModel.objects.filter(modified_by_id=user_id)
                daily_check_data = [daily_check['daily_check_id'] for daily_check in daily_checks.values('daily_check_id')]

                #Filter AssetDisposalFile instances based on created_by_id user ID
                disposal_files = AssetDisposalFile.objects.filter(created_by_id=user_id)
                disposal_file_data = [disposal_files['file_id'] for disposal_file in disposal_files.values('file_id')]

                # Filter DisposalModel instances based on created_by or modified_by user ID
                disposals = AssetDisposalModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                disposal_data = [disposal['id'] for disposal in disposals.values('id')]

                # Filter AssetFile instances based on uploaded_by user ID
                asset_files = AssetFile.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_file_data = [asset_file['file_id'] for asset_file in asset_files.values('file_id')]

                # Filter AssetIssueCategory instances based on created_by or modified_by user ID 
                issue_categories = AssetIssueCategory.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                issue_category_data = [category['id'] for category in issue_categories.values('id')]

                # Filter AssetIssueModel instances based on created_by or modified_by user ID
                asset_issues = AssetIssueModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_issue_data = [asset_issue['issue_id'] for asset_issue in asset_issues.values('issue_id')]

                # Filter AssetLog instances based on user ID
                asset_logs = AssetLog.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_log_data = [asset_log['asset_log_id'] for asset_log in asset_logs.values('asset_log_id')]

                # Filter AssetManufactureModel instances based on created_by or modified_by user ID
                asset_manufactures = AssetManufacturerModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_manufacture_data = [manufacture['id'] for manufacture in asset_manufactures.values('id')]

                # Filter AssetModel instances based on created_by or modified_by user ID
                assets = AssetModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_data = [asset['VIN'] for asset in assets.values('VIN')]

                # Filter AssetRequestModel instances based on created_by or modified_by user ID
                asset_requests = AssetRequestModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_request_data = [asset_request['id'] for asset_request in asset_requests.values('id')]

                # Filter AssetTransfer Model instances based on created_by or modified_by user ID
                asset_transfers = AssetTransfer.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_transfer_data = [asset_transfer['asset_transfer_id'] for asset_transfer in asset_transfers.values('asset_transfer_id')]

                # Filter AssetType Model instances based on created_by or modified_by user ID
                asset_types = AssetTypeModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_type_data = [asset_type['id'] for asset_type in asset_types.values('id')]

                # Filter AssetTypeChecks instances based on created_by or modified_by user ID
                asset_type_checks = AssetTypeChecks.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                asset_type_check_data = [asset_type_check['id'] for asset_type_check in asset_type_checks.values('id')]

                # Filter DeliveryCost Model instances based on created_by or modified_by user ID
                delivery_costs = DeliveryCost.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                delivery_cost_data = [delivery_cost['id'] for delivery_cost in delivery_costs.values('id')]

                # Filter ErrorReport Model instances based on created_by or modified_by user ID
                error_reports = ErrorReport.objects.filter(created_by_id=user_id)
                error_report_data = [error_report['error_report_id'] for error_report in error_reports.values('error_report_id')]

                # Filter EquipmentTypeModel instances based on created_by or modified_by user ID    
                equipment_types = EquipmentTypeModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                equipment_type_data = [equipment_type['equipment_type_id'] for equipment_type in equipment_types.values('equipment_type_id')]

                # Filter FuelCost Model instances based on created_by or modified_by user ID
                fuel_costs = FuelCost.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                fuel_cost_data = [fuel_cost['id'] for fuel_cost in fuel_costs.values('id')]

                # Filter FuelType Model instances based on created_by or modified_by user ID
                fuel_types = FuelType.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                fuel_type_data = [fuel_type['id'] for fuel_type in fuel_types.values('id')]

                # Filter InsuranceCost Model instances based on created_by or modified_by user ID     
                insurance_costs = InsuranceCost.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                insurance_cost_data = [insurance_cost['id'] for insurance_cost in insurance_costs.values('id')]

                # Filter LaborCost Model instances based on created_by or modified_by user ID
                labor_costs = LaborCost.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                labor_cost_data = [labor_cost['id'] for labor_cost in labor_costs.values('id')]

                # Filter LicenseCost Model instances based on created_by or modified_by user ID
                license_costs = LicenseCost.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                license_cost_data = [license_cost['id'] for license_cost in license_costs.values('id')]

                # Filter MaintenanceForecastRules instances based on created_by or modified_by user ID
                maintenance_rules = MaintenanceForecastRules.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                maintenance_rule_data = [maintenance_rule['id'] for maintenance_rule in maintenance_rules.values('id')]

                # Filter MaintenanceRequestFile instances based on created_by or modified_by user ID
                maintenance_request_files = MaintenanceRequestFile.objects.filter(created_by_id=user_id)
                maintenance_request_file_data = [maintenance_request_file['file_id'] for maintenance_request_file in maintenance_request_files.values('file_id')]

                # Filter MaintenanceRequestModel instances based on created_by or modified_by user ID
                maintenance_requests = MaintenanceRequestModel.objects.filter(created_by_id=user_id)
                maintenance_request_data = [maintenance_request['maintenance_id'] for maintenance_request in maintenance_requests.values('maintenance_id')]

                # Filter Parts instances based on created_by or modified_by user ID
                parts = Parts.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                part_data = [part['id'] for part in parts.values('id')]

                # Filter RentalCost Model instances based on created_by or modified_by user ID
                rental_costs = RentalCost.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                rental_cost_data = [rental_cost['id'] for rental_cost in rental_costs.values('id')]

                # Filter RepairFile instances based on uploaded_by user ID
                repair_files = RepairFile.objects.filter(created_by_id=user_id)
                repair_file_data = [repair_file['file_id'] for repair_file in repair_files.values('file_id')]

                #Filter RepairsModel instances based on created_by or modified_by user ID 
                repairs = RepairsModel.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                repair_data = [repair['repair_id'] for repair in repairs.values('repair_id')]

                # Filter TransferFile instances based on uploaded_by user ID
                transfer_files = TransferFile.objects.filter(created_by_id=user_id)
                transfer_file_data = [transfer_file['file_id'] for transfer_file in transfer_files.values('file_id')]

                #Filter DailyInspectionModel intances based on created_by and modified_by user ID
                daily_inspections = DailyInspection.objects.filter(Q(created_by_id=user_id) | Q(modified_by_id=user_id))
                daily_inspection_data = [daily_inspection['id'] for daily_inspection in daily_inspections.values('id')]

            return Response(
                {
                    "accident": {
                        "accident_id": accident_data
                    },
                    "acquisition_cost": {
                        "id": acquisition_cost_data
                    },
                    "approval": {
                        "approval_id": approval_data
                    },
                    "daily_check": {
                        "daily_check_id": daily_check_data
                    },
                    "disposal_File":{
                        "file_id": disposal_file_data
                    },
                    "disposal_Model": {
                        "disposal_id": disposal_data
                    },
                    "asset_file": {
                        "asset_file_id": asset_file_data
                    },
                    "issue_category": {
                        "id": issue_category_data
                    },
                    "asset_issue": {
                        "asset_issue_id": asset_issue_data
                    },
                    "asset_log": {
                        "asset_log_id": asset_log_data
                    },
                    "asset_manufacture": {
                        "id": asset_manufacture_data
                    },
                    "asset": {
                        "VIN": asset_data
                    },
                    "asset_request": {
                        "id": asset_request_data
                    },
                    "asset_transfer": {
                        "asset_transfer_id": asset_transfer_data
                    },
                    "asset_type": {
                        "id": asset_type_data
                    },
                    "asset_type_check": {
                        "id": asset_type_check_data
                    },
                    "delivery_cost": {
                        "id": delivery_cost_data
                    },
                    "error_report": {
                        "error_report_id": error_report_data
                    },
                    "equipment_type": {
                        "equipment_type_id": equipment_type_data
                    },
                    "fuel_cost": {
                        "id": fuel_cost_data
                    },
                    "fuel_type": {
                        "id": fuel_type_data
                    },
                    "insurance_cost": {
                        "id": insurance_cost_data
                    },
                    "labor_cost": {
                        "id": labor_cost_data
                    },
                    "license_cost": {
                        "id": license_cost_data
                    },
                    "maintenance_rule": {
                        "id": maintenance_rule_data
                    },
                    "maintenance_request_file": {
                        "file_id": maintenance_request_file_data
                    },
                    "maintenance_request": {
                        "maintenance_id": maintenance_request_data
                    },
                    "part": {
                        "id": part_data
                    },
                    "rental_cost": {
                        "id": rental_cost_data
                    },
                    "repair_file": {
                        "file_id": repair_file_data
                    },
                    "repair": {
                        "repair_id": repair_data
                    },
                    "transfer_file": {
                        "id": transfer_file_data
                    },
                    "daily_inspection": {
                        "id": daily_inspection_data
                    }
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# Update user image
class UpdateUserImage(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
            db_name = request.user.db_access
            image = request.FILES.getlist('image')
            user_obj = UserHelper.get_user(request.user.id)
            detailed_user_obj = UserHelper.get_detailed_user_obj(request.user.email, db_name)
            blob_container = "users/images"
            # -------------- Verify file type ---------------
            if(not ImageManager.verify_files_are_images(image)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_1))
                return Response(CustomError.get_full_error_json(CustomError.IUF_1), status=status.HTTP_400_BAD_REQUEST)

            # ------------ Upload file to blob --------------
            company_name = detailed_user_obj.company.company_name
            image_status, file_info = BlobStorageHelper.write_file_to_blob(image[0], blob_container, "user_", company_name, db_name)
            if(not image_status):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)

            # ------------ Delete old image blob ------------
            if("placeholder" not in detailed_user_obj.image_url):
                deletion_status = BlobStorageHelper.delete_file_from_blob(HelperMethods.name_from_end_of_url(detailed_user_obj.image_url, blob_container), blob_container, db_name)
                '''if(not deletion_status):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.IDF_0))
                    return Response(CustomError.get_full_error_json(CustomError.IDF_0), status=status.HTTP_400_BAD_REQUEST)'''

            # ----------- Upload file url to DB --------------
            if(not UserFileActions.create_user_image_record(detailed_user_obj, file_info.file_url)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)

            # create user record
            if(not UserHistory.create_user_record(user_obj.id)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)
            # Create detailed user record
            if(not DetailedUserHistory.create_detailed_user_record(detailed_user_obj.detailed_user_id, db_name)):
                Logger.getLogger().error(CustomError.MHF_5)
                return Response(CustomError.get_full_error_json(CustomError.MHF_5), status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# Superuser updates their own permission - Developed for dev team
class UserPermissionSuperUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_user_permission(request.data, request.user)
        

# Superuser gets any user information
class GetAnyUserInfoSuperUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_get_any_user_information(request.data, request.user)
        

# #superusers can edit account information of any user
class EditAnyUserInfoSuperUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_edit_any_user_account(request.data, request.user)

#  #superuser can generate any user's password
class CreateUserPasswordSuperuser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_random_password_generate(request.data, request.user)


# Toggle the agreement_accepeted variable in the detailed user model
class UpdateAgreement(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_update_agreement(request.data, request.user)

# Update user config
class UpdateUserConfiguration(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_update_user_config(request.data, request.user)
    
# Append to the user tablefilters
class UpdateUserTableFilter(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_update_user_tablefilter(request.data, request.user)
        
# Delete from the user tablefilters
class DeleteUserTableFilter(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        return UserHandler.handle_delete_user_tablefilter(request.data, request.user)