import logging

from rest_framework import status
from rest_framework.response import Response

from GSE_Backend.errors.ErrorDictionary import CustomError
from api.Models.maintenance_forecast import MaintenanceForecastRules
from core.AssetManager.AssetHelper import AssetHelper
from .MaintenanceForecastHelper import MaintenanceForecastHelper
from ..Helper import HelperMethods
from ..InspectionTypeManager.InspectionTypeHelper import InspectionTypeHelper


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceForecastUpdater:

    @staticmethod
    def update_full_maintenance_rule(validated_data, db_name):
        try:
            maintenance_rule_obj = MaintenanceForecastHelper.get_maintenance_forecast_rule_by_vin_and_type(
                validated_data.get('VIN'), validated_data.get('inspection_type'), validated_data.get('linked_engine'),
                db_name)
            if not len(str(validated_data.get("hour_cycle"))) == 0 and validated_data.get("hour_cycle") is not None:
                maintenance_rule_obj.hour_cycle = validated_data.get('hour_cycle')
            if not len(str(validated_data.get("mileage_cycle"))) == 0 and validated_data.get(
                    "mileage_cycle") is not None:
                maintenance_rule_obj.mileage_cycle = validated_data.get('mileage_cycle')
            if not len(str(validated_data.get("time_cycle"))) == 0 and validated_data.get("time_cycle") is not None:
                maintenance_rule_obj.time_cycle = validated_data.get('time_cycle')

            maintenance_rule_obj.save()

            return maintenance_rule_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e),
                                  status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_maintenance_rule_entry(maintenance_rule, detailed_user, db_name):
        asset = AssetHelper.get_asset_by_VIN(maintenance_rule.get("VIN"), db_name)
        inspection_type, inspection_type_response = InspectionTypeHelper.get_inspection_type_by_code(
            maintenance_rule.get("inspection_code"), db_name)
        return MaintenanceForecastRules(
            VIN=asset,
            inspection_type=inspection_type,
            created_by=detailed_user,
            modified_by=detailed_user,
            hour_cycle=HelperMethods.string_to_integer_with_default(maintenance_rule.get("hour_cycle")),
            mileage_cycle=HelperMethods.string_to_integer_with_default(maintenance_rule.get("mileage_cycle")),
            time_cycle=HelperMethods.string_to_integer_with_default(maintenance_rule.get("time_cycle")),
        )
