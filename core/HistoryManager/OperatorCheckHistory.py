from rest_framework.response import Response
from rest_framework import status
from .AssetHistory import AssetHistory
from api.Models.asset_daily_checks_history import AssetDailyChecksModelHistory
from api.Models.asset_log import AssetLog
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)
   
    
class OperatorCheckHistory():

    @staticmethod
    def create_daily_check_record_by_obj(daily_check_obj):
        try:
            daily_check_history_entry = OperatorCheckHistory.generate_daily_check_history_entry(daily_check_obj)
            daily_check_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_daily_check_history_entry(daily_check):
        return AssetDailyChecksModelHistory(
            daily_check = daily_check,
            custom_id=daily_check.custom_id,
            operable = daily_check.operable,
            mileage = daily_check.mileage,
            hours = daily_check.hours,
            is_tagout = daily_check.is_tagout,
            location=daily_check.location,
            modified_by = daily_check.modified_by,
            tires = daily_check.tires,
            wheels = daily_check.wheels,
            horn = daily_check.horn,
            fuel = daily_check.fuel,
            mirrors = daily_check.mirrors,
            glass = daily_check.glass,
            overhead_guard = daily_check.overhead_guard,
            steps = daily_check.steps,
            forks = daily_check.forks,
            operator_cab = daily_check.operator_cab,
            cosmetic_damage = daily_check.cosmetic_damage,
            brakes = daily_check.brakes,
            steering = daily_check.steering,
            attachments = daily_check.attachments,
            mud_flaps = daily_check.mud_flaps,
            electrical_connectors = daily_check.electrical_connectors,
            air_pressure = daily_check.air_pressure,
            boom_extensions = daily_check.boom_extensions,
            spreader_functions = daily_check.spreader_functions,
            headlights = daily_check.headlights,
            backup_lights = daily_check.backup_lights,
            trailer_light_cord = daily_check.trailer_light_cord,
            oil = daily_check.oil,
            transmission_fluid = daily_check.transmission_fluid,
            steering_fluid = daily_check.steering_fluid,
            hydraulic_fluid = daily_check.hydraulic_fluid,
            brake_fluid = daily_check.brake_fluid,
            fire_extinguisher = daily_check.fire_extinguisher,
            hydraulic_hoses = daily_check.hydraulic_hoses,
            trailer_air_lines = daily_check.trailer_air_lines,
            other_leaks = daily_check.other_leaks
        )

    @staticmethod
    def create_operator_check_event_log(op_check_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(op_check_obj.VIN, AssetLog.operator_check, op_check_obj.custom_id, op_check_obj.modified_by, description, op_check_obj.location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_10, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_10, e), status=status.HTTP_400_BAD_REQUEST)