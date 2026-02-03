from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_type_checks import AssetTypeChecks
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging
from api.Models.asset_type_checks_history import AssetTypeChecksHistory

from core.Helper import HelperMethods

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeChecksHelper():

    @staticmethod
    def get_all_asset_type_checks(db_name):
        return AssetTypeChecks.objects.using(db_name).all()

    @staticmethod
    def get_checks_by_asset_type(asset_type, db_name):
        try:
            return AssetTypeChecks.objects.using(db_name).get(asset_type_name=asset_type)
        except Exception as e:
            return None

    @staticmethod
    def get_checks_by_id(checks_id, db_name):
        try:
            return AssetTypeChecks.objects.using(db_name).get(id=checks_id)
        except Exception as e:
            return None

    @staticmethod
    def check_if_atleast_one_content_field(asset_type_checks_data, content_fields):
        for field in content_fields:
            if HelperMethods.validate_bool(asset_type_checks_data.get(field)):
                return True
        return False

    @staticmethod
    def asset_type_checks_exist_by_id(checks_id, db_name):
        return AssetTypeChecks.objects.using(db_name).filter(pk=checks_id).exists()

    # If atleast one of the listed fields is True, then lights is True too.
    @staticmethod
    def get_lights_bool(asset_type_checks_data):
        content_fields = ["headlights", "backup_lights", "trailer_light_cord"]
        return AssetTypeChecksHelper.check_if_atleast_one_content_field(asset_type_checks_data, content_fields)

    # If atleast one of the listed fields is True, then fluids is True too.
    @staticmethod
    def get_fluids_bool(asset_type_checks_data):
        content_fields = ["oil", "transmission_fluid", "steering_fluid", "hydraulic_fluid", "brake_fluid"]
        return AssetTypeChecksHelper.check_if_atleast_one_content_field(asset_type_checks_data, content_fields)

    # If atleast one of the listed fields is True, then safety_equipment is True too.
    @staticmethod
    def get_safety_equipment_bool(asset_type_checks_data):
        content_fields = ["fire_extinguisher"]
        return AssetTypeChecksHelper.check_if_atleast_one_content_field(asset_type_checks_data, content_fields)

    # If atleast one of the listed fields is True, then leaks is True too.
    @staticmethod
    def get_leaks_bool(asset_type_checks_data):
        content_fields = ["hydraulic_hoses", "trailer_air_lines", "other_leaks"]
        return AssetTypeChecksHelper.check_if_atleast_one_content_field(asset_type_checks_data, content_fields)

    @staticmethod
    def get_all_asset_type_checks_fields():
        all_fields = AssetTypeChecks._meta.fields
        return [str(h).split('.')[2] for h in all_fields]

    @staticmethod
    def get_asset_type_checks_for_daterange(start_date, end_date, db_name):
        return AssetTypeChecks.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_asset_type_checks_history_for_daterange(start_date, end_date, db_name):
        return AssetTypeChecksHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def update_asset_type_check_dict(request_data, detailed_user):
        request_data["created_by"] = detailed_user.detailed_user_id
        request_data["modified_by"] = detailed_user.detailed_user_id
        return request_data