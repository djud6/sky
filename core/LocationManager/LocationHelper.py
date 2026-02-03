from django import db
from rest_framework.response import Response
from rest_framework import status
from api.Models.locations import LocationModel
from api.Models.Snapshot.snapshot_daily_location_cost import SnapshotDailyLocationCost
from api.Models.RolePermissions import RolePermissions
from core.UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class LocationHelper():

    @staticmethod
    def select_related_to_location(qs):
        return qs.select_related('location', 'currency')

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_all_locations(db_name):
        return LocationModel.objects.using(db_name).all()

    @staticmethod
    def get_all_locations_for_user(user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        all_locations = LocationHelper.get_all_locations(user.db_access)
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return all_locations

        user_location_ids = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return all_locations.filter(location_id__in=user_location_ids)

    @staticmethod
    def get_location_by_name(location_name, db_name):
        return LocationModel.objects.using(db_name).get(location_name=location_name)

    @staticmethod
    def get_location_by_id(location_id, db_name):
        try:
            return LocationModel.objects.using(db_name).get(location_id=location_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.LDE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.LDE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_location_id_by_name(location_name, db_name):
        return LocationModel.objects.using(db_name).filter(location_name=location_name).values_list("location_id", flat=True)[0]
           
    @staticmethod
    def get_fuel_cost_by_location(location, db_name):
        return SnapshotDailyLocationCost.objects.using(db_name).filter(location=location).order_by('location', 'date_created')

    # --------------------------------------------------------------------------------------

    @staticmethod
    def location_exists_by_name(location_name, db_name):
        return LocationModel.objects.using(db_name).filter(location_name=location_name).exists()