from django.core.mail.message import sanitize_address
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_daily_checks import AssetDailyChecksModel
from api.Models.asset_daily_checks_comment import AssetDailyChecksComment
from api.Models.DetailedUser import DetailedUser
from ..UserManager.UserHelper import UserHelper
from ..HistoryManager.OperatorCheckHistory import OperatorCheckHistory
from ..Helper import HelperMethods
from ..AssetManager.AssetUpdater import AssetUpdater
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DailyOperationalCheckUpdater():

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_op_check_post_creation(daily_op_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            daily_op_obj.created_by = detailed_user
            daily_op_obj.modified_by = detailed_user
            daily_op_obj.custom_id = str(detailed_user.company.company_name).replace(' ', '-') + "-dc-" + str(daily_op_obj.daily_check_id)
            daily_op_obj.save()
            return daily_op_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_1, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_1, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_op_check_modified_by(daily_op_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            daily_op_obj.modified_by = detailed_user
            daily_op_obj.save()
            return daily_op_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_1, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_1, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def delete_daily_op_check(daily_op_check_obj, db_name):
        AssetDailyChecksModel.objects.using(db_name).filter(daily_check_id=daily_op_check_obj.daily_check_id).delete()

    # --------------------------------------------------------------------------------------

    @staticmethod
    def add_daily_check_comments(comments, daily_op_check_obj, db_name):
        try:
            comment_entries = []
            for comment in comments:
                comment_entries.append(DailyOperationalCheckUpdater.create_daily_check_comment_entry(comment, daily_op_check_obj))

            AssetDailyChecksComment.objects.using(db_name).bulk_create(comment_entries)

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.DOCI_4, e)
            return Response(CustomError.get_full_error_json(CustomError.DOCI_4, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------
    
    @staticmethod
    def create_daily_check_comment_entry(comment, daily_op_check_obj):
        return AssetDailyChecksComment(
            daily_check=daily_op_check_obj,
            comment=comment.get("comment"),
            check=comment.get("check")
        )

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_daily_operator_check(daily_check_entry, request_data, user):
        try:
            old_values = {}
            is_important = False
            if not len(str(request_data.get("mileage"))) == 0 and request_data.get("mileage") is not None:
                old_values["mileage"] = daily_check_entry.mileage
                daily_check_entry.mileage = request_data.get("mileage")
                is_important = True
            if not len(str(request_data.get("hours"))) == 0 and request_data.get("hours") is not None:
                old_values["hours"] = daily_check_entry.hours
                daily_check_entry.hours = request_data.get("hours")
                is_important = True
            if not len(str(request_data.get("fuel"))) == 0 and request_data.get("fuel") is not None:
                old_values["fuel"] = daily_check_entry.fuel
                daily_check_entry.fuel = request_data.get("fuel")
                is_important = True

            if not len(str(request_data.get("is_tagout"))) == 0 and request_data.get("is_tagout") is not None:
                # TODO: May need to set asset to inop if this daily check is the latest one.
                daily_check_entry.is_tagout = HelperMethods.validate_bool(request_data.get("is_tagout"))
            if not len(str(request_data.get("operable"))) == 0 and request_data.get("operable") is not None:
                daily_check_entry.operable = HelperMethods.validate_bool(request_data.get("operable"))
            if not len(str(request_data.get("tires"))) == 0 and request_data.get("tires") is not None:
                daily_check_entry.tires = HelperMethods.validate_bool(request_data.get("tires"))
            if not len(str(request_data.get("wheels"))) == 0 and request_data.get("wheels") is not None:
                daily_check_entry.wheels = HelperMethods.validate_bool(request_data.get("wheels"))
            if not len(str(request_data.get("horn"))) == 0 and request_data.get("horn") is not None:
                daily_check_entry.horn = HelperMethods.validate_bool(request_data.get("horn"))
            if not len(str(request_data.get("mirrors"))) == 0 and request_data.get("mirrors") is not None:
                daily_check_entry.mirrors = HelperMethods.validate_bool(request_data.get("mirrors"))
            if not len(str(request_data.get("glass"))) == 0 and request_data.get("glass") is not None:
                daily_check_entry.glass = HelperMethods.validate_bool(request_data.get("glass"))
            if not len(str(request_data.get("overhead_guard"))) == 0 and request_data.get("overhead_guard") is not None:
                daily_check_entry.overhead_guard = HelperMethods.validate_bool(request_data.get("overhead_guard"))
            if not len(str(request_data.get("steps"))) == 0 and request_data.get("steps") is not None:
                daily_check_entry.steps = HelperMethods.validate_bool(request_data.get("steps"))
            if not len(str(request_data.get("forks"))) == 0 and request_data.get("forks") is not None:
                daily_check_entry.forks = HelperMethods.validate_bool(request_data.get("forks"))
            if not len(str(request_data.get("operator_cab"))) == 0 and request_data.get("operator_cab") is not None:
                daily_check_entry.operator_cab = HelperMethods.validate_bool(request_data.get("operator_cab"))
            if not len(str(request_data.get("cosmetic_damage"))) == 0 and request_data.get("cosmetic_damage") is not None:
                daily_check_entry.cosmetic_damage = HelperMethods.validate_bool(request_data.get("cosmetic_damage"))
            if not len(str(request_data.get("brakes"))) == 0 and request_data.get("brakes") is not None:
                daily_check_entry.brakes = HelperMethods.validate_bool(request_data.get("brakes"))
            if not len(str(request_data.get("steering"))) == 0 and request_data.get("steering") is not None:
                daily_check_entry.steering = HelperMethods.validate_bool(request_data.get("steering"))
            if not len(str(request_data.get("attachments"))) == 0 and request_data.get("attachments") is not None:
                daily_check_entry.attachments = HelperMethods.validate_bool(request_data.get("attachments"))
            if not len(str(request_data.get("mud_flaps"))) == 0 and request_data.get("mud_flaps") is not None:
                daily_check_entry.mud_flaps = HelperMethods.validate_bool(request_data.get("mud_flaps"))
            if not len(str(request_data.get("electrical_connectors"))) == 0 and request_data.get("electrical_connectors") is not None:
                daily_check_entry.electrical_connectors = HelperMethods.validate_bool(request_data.get("electrical_connectors"))
            if not len(str(request_data.get("air_pressure"))) == 0 and request_data.get("air_pressure") is not None:
                daily_check_entry.air_pressure = HelperMethods.validate_bool(request_data.get("air_pressure"))
            if not len(str(request_data.get("boom_extensions"))) == 0 and request_data.get("boom_extensions") is not None:
                daily_check_entry.boom_extensions = HelperMethods.validate_bool(request_data.get("boom_extensions"))
            if not len(str(request_data.get("spreader_functions"))) == 0 and request_data.get("spreader_functions") is not None:
                daily_check_entry.spreader_functions = HelperMethods.validate_bool(request_data.get("spreader_functions"))
            if not len(str(request_data.get("headlights"))) == 0 and request_data.get("headlights") is not None:
                daily_check_entry.headlights = HelperMethods.validate_bool(request_data.get("headlights"))
            if not len(str(request_data.get("backup_lights"))) == 0 and request_data.get("backup_lights") is not None:
                daily_check_entry.backup_lights = HelperMethods.validate_bool(request_data.get("backup_lights"))
            if not len(str(request_data.get("trailer_light_cord"))) == 0 and request_data.get("trailer_light_cord") is not None:
                daily_check_entry.trailer_light_cord = HelperMethods.validate_bool(request_data.get("trailer_light_cord"))
            if not len(str(request_data.get("oil"))) == 0 and request_data.get("oil") is not None:
                daily_check_entry.oil = HelperMethods.validate_bool(request_data.get("oil"))
            if not len(str(request_data.get("transmission_fluid"))) == 0 and request_data.get("transmission_fluid") is not None:
                daily_check_entry.transmission_fluid = HelperMethods.validate_bool(request_data.get("transmission_fluid"))
            if not len(str(request_data.get("steering_fluid"))) == 0 and request_data.get("steering_fluid") is not None:
                daily_check_entry.steering_fluid = HelperMethods.validate_bool(request_data.get("steering_fluid"))
            if not len(str(request_data.get("hydraulic_fluid"))) == 0 and request_data.get("hydraulic_fluid") is not None:
                daily_check_entry.hydraulic_fluid = HelperMethods.validate_bool(request_data.get("hydraulic_fluid"))
            if not len(str(request_data.get("brake_fluid"))) == 0 and request_data.get("brake_fluid") is not None:
                daily_check_entry.brake_fluid = HelperMethods.validate_bool(request_data.get("brake_fluid"))
            if not len(str(request_data.get("fire_extinguisher"))) == 0 and request_data.get("fire_extinguisher") is not None:
                daily_check_entry.fire_extinguisher = HelperMethods.validate_bool(request_data.get("fire_extinguisher"))
            if not len(str(request_data.get("hydraulic_hoses"))) == 0 and request_data.get("hydraulic_hoses") is not None:
                daily_check_entry.hydraulic_hoses = HelperMethods.validate_bool(request_data.get("hydraulic_hoses"))
            if not len(str(request_data.get("trailer_air_lines"))) == 0 and request_data.get("trailer_air_lines") is not None:
                daily_check_entry.trailer_air_lines = HelperMethods.validate_bool(request_data.get("trailer_air_lines"))
            if not len(str(request_data.get("other_leaks"))) == 0 and request_data.get("other_leaks") is not None:
                daily_check_entry.other_leaks = HelperMethods.validate_bool(request_data.get("other_leaks"))
                
            daily_check_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)        

            return daily_check_entry, old_values, is_important, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.TUF_10, e)
            return daily_check_entry, old_values, is_important, Response(CustomError.get_full_error_json(CustomError.TUF_10, e), status=status.HTTP_400_BAD_REQUEST)