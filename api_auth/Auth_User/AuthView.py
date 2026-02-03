from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from ..Serializers.serializers import LinkedUserModelSerializer, DetailedUserSerializer, UserConfigurationSerializer
from core.UserManager.UserHelper import UserHelper
from core.UserManager.UserUpdater import UserUpdater
from core.AssetManager.AssetHandler import AssetHandler
from core.LocationManager.LocationHandler import LocationHandler
from core.BusinessUnitManager.BusinessUnitHandler import BusinessUnitHandler
from core.AssetRequestManager.AssetRequestHandler import AssetRequestHandler
from core.MaintenanceManager.MaintenanceHandler import MaintenanceHandler
from core.CostManager.CostHandler import UnitChoicesHandler
from core.IssueCategoryManager.IssueCategoryHandler import IssueCategoryHandler
from core.AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from api.Models.Company import Company
from GSE_Backend.errors.ErrorDictionary import CustomError
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from rest_framework import status
from .db_constants import Constants
import logging
from .AuthViewHelper import token_expire_login_handler, expires_in
from datetime import timedelta
from django.conf import settings
from core.CostCentreManager.CostCentreHandler import CostCentreHandler
from core.UserTableLayoutManager.UserTableLayoutHandler import UserTableLayoutHandler

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.using(Constants.AUTH_DB).get_or_create(user=user)
            is_expired, token = token_expire_login_handler(token)
            token_expiration = token.created + timedelta(seconds = settings.TOKEN_EXPIRED_AFTER_SECONDS)

            user = UserUpdater.update_user_last_login(UserHelper.get_user(user.id))


            session_info = {
                'token': token.key,
                'token_expiration': token_expiration,
                'success': True,
                'message': 'Login successful',
            }
            
            
            detailed_user_info = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            
            # >>>>> CORREÇÃO APLICADA AQUI <<<<<
            session_info['user'] = LinkedUserModelSerializer(user).data
            session_info['detailed_user'] = DetailedUserSerializer(detailed_user_info).data
            # >>>>> FIM DA CORREÇÃO <<<<<
            
            user_role = detailed_user_info.role_permissions.role if hasattr(detailed_user_info, 'role_permissions') else 'user'
            
            # Server-side redirect logic
            if user_role == 'supervisor':
                redirect_url = '/supervisor-dashboard'
            elif user_role == 'admin':
                redirect_url = '/admin-dashboard'
            else:
                redirect_url = '/dashboard'
            
            session_info['redirect_url'] = redirect_url
            
        
            try:
                return Response(session_info, status=status.HTTP_200_OK)
            except Exception as e:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                return Response(CustomError.get_full_error_json(CustomError.G_0, e), 
                               status=status.HTTP_400_BAD_REQUEST)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IL_0))
            Logger.getLogger().error(serializer.errors)
            return Response(CustomError.get_full_error_json(CustomError.IL_0), 
                           status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def aux_data(user):
        try:
            # locations
            locations_response = LocationHandler.handle_list_locations(user)
            if locations_response.status_code != status.HTTP_200_OK:
                return None, locations_response
            locations = locations_response.data

            # business units
            business_units_response = BusinessUnitHandler.handle_get_business_units_for_user(user)
            if business_units_response.status_code != status.HTTP_200_OK:
                return None, business_units_response
            business_units = business_units_response.data

            # asset request justifications
            asset_request_justifications_response = AssetRequestHandler.handle_get_justifications(user)
            if asset_request_justifications_response.status_code != status.HTTP_200_OK:
                return None, asset_request_justifications_response
            asset_request_justifications = asset_request_justifications_response.data

            # fuel volume units
            volume_units_response = UnitChoicesHandler.handle_get_all_volume_unit_types(user)
            if volume_units_response.status_code != status.HTTP_200_OK:
                return None, volume_units_response
            volume_units = volume_units_response.data

            # currencies
            currencies_response = UnitChoicesHandler.handle_get_all_currency_types(user)
            if currencies_response.status_code != status.HTTP_200_OK:
                return None, currencies_response
            currencies = currencies_response.data

            # job specs
            job_specs_response = AssetHandler.handle_list_job_specification(user)
            if job_specs_response.status_code != status.HTTP_200_OK:
                return None, job_specs_response
            job_specs = job_specs_response.data

            # asset type checks
            asset_type_check_fields = AssetTypeChecksHelper.get_all_asset_type_checks_fields()

            # inspection types
            inspection_types_response = MaintenanceHandler.handle_list_inspections(user)
            if inspection_types_response.status_code != status.HTTP_200_OK:
                return inspection_types_response
            inspection_types = inspection_types_response.data

            # issue categories
            issue_categories_response = IssueCategoryHandler.handle_get_all_categories(user)
            if issue_categories_response.status_code != status.HTTP_200_OK:
                return issue_categories_response
            issue_categories = issue_categories_response.data
            
            cost_centre_response=CostCentreHandler.handle_get_all(user)
            if cost_centre_response.status_code!=status.HTTP_200_OK:
                return cost_centre_response
            cost_centres=cost_centre_response.data
            
            table_layout_response=UserTableLayoutHandler.handle_get_all_dict(user)
            if table_layout_response.status_code!=status.HTTP_200_OK:
                return table_layout_response
            table_layout=table_layout_response.data

            return {
                'locations': locations,
                'business_units': business_units,
                'asset_request_justifications': asset_request_justifications,
                'fuel_volume_units': volume_units,
                'currencies': currencies,
                'job_specifications': job_specs,
                'asset_type_check_fields': asset_type_check_fields,
                'inspection_types': inspection_types,
                'issue_categories': issue_categories,
                'cost_centres':cost_centres,
                'table_layout':table_layout
            }, Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)