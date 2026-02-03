from rest_framework.response import Response
from rest_framework import status
from ..LocationManager.LocationHelper import LocationHelper
from api.Models.business_unit import BusinessUnitModel
from api.Models.RolePermissions import RolePermissions
from ..UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class BusinessUnitHelper():
    
    # This method will take a business unit qs and filter it to only show business units relevant to user
    @staticmethod
    def filter_business_units_for_user(business_unit_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return business_unit_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return business_unit_qs.filter(location__in=user_locations)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_all_business_units(db_name):
        return BusinessUnitModel.objects.using(db_name).all()

    @staticmethod
    def get_business_unit_by_id(business_unit_id, db_name):
        try:
            return BusinessUnitModel.objects.using(db_name).get(business_unit_id=business_unit_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.BUDNE_0))
            return None, Response(CustomError.get_full_error_json(CustomError.BUDNE_0), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_business_unit_by_name(business_unit_name, db_name):
        return BusinessUnitModel.objects.using(db_name).get(name=business_unit_name)

    @staticmethod
    def get_business_unit_by_name_and_location(business_unit_name, location_name, db_name):
        location_id = LocationHelper.get_location_id_by_name(location_name, db_name)
        return BusinessUnitModel.objects.using(db_name).get(name=business_unit_name, location=location_id)

    @staticmethod
    def get_business_unit_id_by_name(business_unit_name, db_name):
        return BusinessUnitModel.objects.using(db_name).filter(name=business_unit_name).values_list('business_unit_id', flat=True)[0]

    @staticmethod
    def get_business_unit_location_id(business_unit_id, db_name):
        try:
            business_unit = BusinessUnitModel.objects.using(db_name).get(business_unit_id=business_unit_id)
            return business_unit.location.location_id, Response(status=status.HTTP_200_OK)
        except BusinessUnitModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.BUDNE_0))
            return None, Response(CustomError.get_full_error_json(CustomError.BUDNE_0), status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    
    

