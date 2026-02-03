from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_type_checks import AssetTypeChecks
from .AssetTypeChecksHelper import AssetTypeChecksHelper
from django.core.exceptions import ObjectDoesNotExist
from ..Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeChecksUpdater():

    @staticmethod
    def create_asset_type_checks_entry(asset_type_checks_data):
        return AssetTypeChecks(
            asset_type_name=asset_type_checks_data.get("asset_type").strip(),
            tires=asset_type_checks_data.get("tires").strip(),
            wheels=asset_type_checks_data.get("wheels").strip(),
            lights=AssetTypeChecksHelper.get_lights_bool(asset_type_checks_data),
            headlights=asset_type_checks_data.get("headlights").strip(),
            backup_lights=asset_type_checks_data.get("backup_lights").strip(),
            trailer_light_cord=asset_type_checks_data.get("trailer_light_cord").strip(),
            horn=asset_type_checks_data.get("horn").strip(),
            fluids=AssetTypeChecksHelper.get_fluids_bool(asset_type_checks_data),
            oil=asset_type_checks_data.get("oil").strip(),
            transmission_fluid=asset_type_checks_data.get("transmission_fluid").strip(),
            steering_fluid=asset_type_checks_data.get("steering_fluid").strip(),
            hydraulic_fluid=asset_type_checks_data.get("hydraulic_fluid").strip(),
            brake_fluid=asset_type_checks_data.get("brake_fluid").strip(),
            fuel=asset_type_checks_data.get("fuel").strip(),
            mirrors=asset_type_checks_data.get("mirrors").strip(),
            glass=asset_type_checks_data.get("glass").strip(),
            safety_equipment=AssetTypeChecksHelper.get_safety_equipment_bool(asset_type_checks_data),
            fire_extinguisher=asset_type_checks_data.get("fire_extinguisher").strip(),
            overhead_guard=asset_type_checks_data.get("overhead_guard").strip(),
            steps=asset_type_checks_data.get("steps").strip(),
            forks=asset_type_checks_data.get("forks").strip(),
            operator_cab=asset_type_checks_data.get("operator_cab").strip(),
            cosmetic_damage=asset_type_checks_data.get("cosmetic_damage").strip(),
            leaks=AssetTypeChecksHelper.get_leaks_bool(asset_type_checks_data),
            hydraulic_hoses=asset_type_checks_data.get("hydraulic_hoses").strip(),
            trailer_air_lines=asset_type_checks_data.get("trailer_air_lines").strip(),
            other_leaks=asset_type_checks_data.get("other_leaks").strip(),
            brakes=asset_type_checks_data.get("brakes").strip(),
            steering=asset_type_checks_data.get("steering").strip(),
            attachments=asset_type_checks_data.get("attachments").strip(),
            mud_flaps=asset_type_checks_data.get("mud_flaps").strip(),
            electrical_connectors=asset_type_checks_data.get("electrical_connectors").strip(),
            air_pressure=asset_type_checks_data.get("air_pressure").strip(),
            boom_extensions=asset_type_checks_data.get("boom_extensions").strip(),
            spreader_functions=asset_type_checks_data.get("spreader_functions").strip()
        )

    @staticmethod
    def update_asset_type_checks_fields(checks_obj, request_data, detailed_user):
        try:
            if not len(str(request_data.get("tires"))) == 0 and request_data.get("tires") is not None:
                checks_obj.tires = HelperMethods.validate_bool(request_data.get("tires"))
            if not len(str(request_data.get("wheels"))) == 0 and request_data.get("wheels") is not None:
                checks_obj.wheels = HelperMethods.validate_bool(request_data.get("wheels"))
            if not len(str(request_data.get("headlights"))) == 0 and request_data.get("headlights") is not None:
                checks_obj.headlights = HelperMethods.validate_bool(request_data.get("headlights"))
            if not len(str(request_data.get("backup_lights"))) == 0 and request_data.get("backup_lights") is not None:
                checks_obj.backup_lights = HelperMethods.validate_bool(request_data.get("backup_lights"))
            if not len(str(request_data.get("trailer_light_cord"))) == 0 and request_data.get("trailer_light_cord") is not None:
                checks_obj.trailer_light_cord = HelperMethods.validate_bool(request_data.get("trailer_light_cord"))
            if not len(str(request_data.get("horn"))) == 0 and request_data.get("horn") is not None:
                checks_obj.horn = HelperMethods.validate_bool(request_data.get("horn"))
            if not len(str(request_data.get("oil"))) == 0 and request_data.get("oil") is not None:
                checks_obj.oil = HelperMethods.validate_bool(request_data.get("oil"))
            if not len(str(request_data.get("transmission_fluid"))) == 0 and request_data.get("transmission_fluid") is not None:
                checks_obj.transmission_fluid = HelperMethods.validate_bool(request_data.get("transmission_fluid"))
            if not len(str(request_data.get("steering_fluid"))) == 0 and request_data.get("steering_fluid") is not None:
                checks_obj.steering_fluid = HelperMethods.validate_bool(request_data.get("steering_fluid"))
            if not len(str(request_data.get("hydraulic_fluid"))) == 0 and request_data.get("hydraulic_fluid") is not None:
                checks_obj.hydraulic_fluid = HelperMethods.validate_bool(request_data.get("hydraulic_fluid"))
            if not len(str(request_data.get("brake_fluid"))) == 0 and request_data.get("brake_fluid") is not None:
                checks_obj.brake_fluid = HelperMethods.validate_bool(request_data.get("brake_fluid"))
            if not len(str(request_data.get("fuel"))) == 0 and request_data.get("fuel") is not None:
                checks_obj.fuel = HelperMethods.validate_bool(request_data.get("fuel"))
            if not len(str(request_data.get("mirrors"))) == 0 and request_data.get("mirrors") is not None:
                checks_obj.mirrors = HelperMethods.validate_bool(request_data.get("mirrors"))
            if not len(str(request_data.get("glass"))) == 0 and request_data.get("glass") is not None:
                checks_obj.glass = HelperMethods.validate_bool(request_data.get("glass"))
            if not len(str(request_data.get("fire_extinguisher"))) == 0 and request_data.get("fire_extinguisher") is not None:
                checks_obj.fire_extinguisher = HelperMethods.validate_bool(request_data.get("fire_extinguisher"))
            if not len(str(request_data.get("overhead_guard"))) == 0 and request_data.get("overhead_guard") is not None:
                checks_obj.overhead_guard = HelperMethods.validate_bool(request_data.get("overhead_guard"))
            if not len(str(request_data.get("steps"))) == 0 and request_data.get("steps") is not None:
                checks_obj.steps = HelperMethods.validate_bool(request_data.get("steps"))
            if not len(str(request_data.get("forks"))) == 0 and request_data.get("forks") is not None:
                checks_obj.forks = HelperMethods.validate_bool(request_data.get("forks"))
            if not len(str(request_data.get("operator_cab"))) == 0 and request_data.get("operator_cab") is not None:
                checks_obj.operator_cab = HelperMethods.validate_bool(request_data.get("operator_cab"))
            if not len(str(request_data.get("cosmetic_damage"))) == 0 and request_data.get("cosmetic_damage") is not None:
                checks_obj.cosmetic_damage = HelperMethods.validate_bool(request_data.get("cosmetic_damage"))
            if not len(str(request_data.get("hydraulic_hoses"))) == 0 and request_data.get("hydraulic_hoses") is not None:
                checks_obj.hydraulic_hoses = HelperMethods.validate_bool(request_data.get("hydraulic_hoses"))
            if not len(str(request_data.get("trailer_air_lines"))) == 0 and request_data.get("trailer_air_lines") is not None:
                checks_obj.trailer_air_lines = HelperMethods.validate_bool(request_data.get("trailer_air_lines"))
            if not len(str(request_data.get("other_leaks"))) == 0 and request_data.get("other_leaks") is not None:
                checks_obj.other_leaks = HelperMethods.validate_bool(request_data.get("other_leaks"))
            if not len(str(request_data.get("brakes"))) == 0 and request_data.get("brakes") is not None:
                checks_obj.brakes = HelperMethods.validate_bool(request_data.get("brakes"))
            if not len(str(request_data.get("steering"))) == 0 and request_data.get("steering") is not None:
                checks_obj.steering = HelperMethods.validate_bool(request_data.get("steering"))
            if not len(str(request_data.get("attachments"))) == 0 and request_data.get("attachments") is not None:
                checks_obj.attachments = HelperMethods.validate_bool(request_data.get("attachments"))
            if not len(str(request_data.get("mud_flaps"))) == 0 and request_data.get("mud_flaps") is not None:
                checks_obj.mud_flaps = HelperMethods.validate_bool(request_data.get("mud_flaps"))
            if not len(str(request_data.get("electrical_connectors"))) == 0 and request_data.get("electrical_connectors") is not None:
                checks_obj.electrical_connectors = HelperMethods.validate_bool(request_data.get("electrical_connectors"))
            if not len(str(request_data.get("air_pressure"))) == 0 and request_data.get("air_pressure") is not None:
                checks_obj.air_pressure = HelperMethods.validate_bool(request_data.get("air_pressure"))
            if not len(str(request_data.get("boom_extensions"))) == 0 and request_data.get("boom_extensions") is not None:
                checks_obj.boom_extensions = HelperMethods.validate_bool(request_data.get("boom_extensions"))
            if not len(str(request_data.get("spreader_functions"))) == 0 and request_data.get("spreader_functions") is not None:
                checks_obj.spreader_functions = HelperMethods.validate_bool(request_data.get("spreader_functions"))
            if not len(str(request_data.get("lifesaving_equipments"))) == 0 and request_data.get("lifesaving_equipments") is not None:
                checks_obj.lifesaving_equipments = HelperMethods.validate_bool(request_data.get("lifesaving_equipments"))
            if not len(str(request_data.get("engine_and_all_mechanical"))) == 0 and request_data.get("engine_and_all_mechanical") is not None:
                checks_obj.engine_and_all_mechanical = HelperMethods.validate_bool(request_data.get("engine_and_all_mechanical"))
            if not len(str(request_data.get("communication"))) == 0 and request_data.get("communication") is not None:
                checks_obj.communication = HelperMethods.validate_bool(request_data.get("communication"))
            if not len(str(request_data.get("steering_and_hydraulics"))) == 0 and request_data.get("steering_and_hydraulics") is not None:
                checks_obj.steering_and_hydraulics = HelperMethods.validate_bool(request_data.get("steering_and_hydraulics"))
            if not len(str(request_data.get("electrical"))) == 0 and request_data.get("electrical") is not None:
                checks_obj.electrical = HelperMethods.validate_bool(request_data.get("electrical"))
            if not len(str(request_data.get("navigation_and_strobe_lights"))) == 0 and request_data.get("navigation_and_strobe_lights") is not None:
                checks_obj.navigation_and_strobe_lights = HelperMethods.validate_bool(request_data.get("navigation_and_strobe_lights"))
            if not len(str(request_data.get("fuel_systems"))) == 0 and request_data.get("fuel_systems") is not None:
                checks_obj.fuel_systems = HelperMethods.validate_bool(request_data.get("fuel_systems"))
            if not len(str(request_data.get("anchoring_system"))) == 0 and request_data.get("anchoring_system") is not None:
                checks_obj.anchoring_system = HelperMethods.validate_bool(request_data.get("anchoring_system"))

            checks_obj = AssetTypeChecksUpdater.update_header_fields(checks_obj, checks_obj.__dict__)

            checks_obj.modified_by = detailed_user

            checks_obj.save()
            return checks_obj, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_13, e))
            return checks_obj, Response(CustomError.get_full_error_json(CustomError.TUF_13, e), status=status.HTTP_400_BAD_REQUEST)

    def update_header_fields(checks_obj, checks_dict):
        checks_obj.lights = AssetTypeChecksHelper.get_lights_bool(checks_dict)
        checks_obj.fluids = AssetTypeChecksHelper.get_fluids_bool(checks_dict)
        checks_obj.safety_equipment = AssetTypeChecksHelper.get_safety_equipment_bool(checks_dict)
        checks_obj.leaks = AssetTypeChecksHelper.get_leaks_bool(checks_dict)
        return checks_obj