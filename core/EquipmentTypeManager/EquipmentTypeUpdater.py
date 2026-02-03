from rest_framework.response import Response
from rest_framework import status
from api.Models.equipment_type import EquipmentTypeModel
from ..CostManager.CostHelper import FuelHelper
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from ..ManufacturerManager.ManufacturerHelper import ManufacturerHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
from ..UserManager.UserHelper import UserHelper
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class EquipmentTypeUpdater():

    @staticmethod
    def create_equipment_type_entry(equipment_type_entry, user):

        try:
            db_name = user.db_access
            asset_type, asset_type_response = AssetTypeHelper.get_asset_type_by_name(equipment_type_entry.get("asset_type").strip(), db_name)
            if asset_type_response.status_code != status.HTTP_302_FOUND:
                return equipment_type_entry, asset_type_response
            manufacturer, manufacturer_response = ManufacturerHelper.get_manufacturer_by_name(equipment_type_entry.get("manufacturer").strip(), db_name)
            if manufacturer_response.status_code != status.HTTP_302_FOUND:
                return equipment_type_entry, manufacturer_response
            fuel = None
            if "fuel_name" in equipment_type_entry:
                fuel, fuel_type_response = FuelHelper.get_fuel_type_by_name(equipment_type_entry.get("fuel_name").strip(), db_name)
                if fuel_type_response.status_code != status.HTTP_302_FOUND:
                    fuel = None
            engine = None
            if "engine" in equipment_type_entry:
                engine = equipment_type_entry.get("engine").strip()
            fuel_tank_capacity, fuel_tank_capacity_unit = None, None
            fuel_tank_capacity = equipment_type_entry.get("fuel_tank_capacity")
            if "fuel_tank_capacity_unit" in equipment_type_entry:
                fuel_tank_capacity_unit = equipment_type_entry.get("fuel_tank_capacity_unit").strip()
            equipment_type_entry = EquipmentTypeModel(
                model_number=equipment_type_entry.get("model_number").strip(),
                engine=engine,
                asset_type=asset_type,
                manufacturer=manufacturer,
                fuel=fuel,
                fuel_tank_capacity=fuel_tank_capacity,
                fuel_tank_capacity_unit=fuel_tank_capacity_unit
            )
            return EquipmentTypeUpdater.update_equipment_type_created_by(equipment_type_entry, user)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ETCF_0, e))
            return equipment_type_entry, Response(CustomError.get_full_error_json(CustomError.ETCF_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------


    @staticmethod
    def update_equipment_type_created_by(equipment_type_entry_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            equipment_type_entry_obj.created_by = detailed_user
            equipment_type_entry_obj.modified_by = detailed_user
            return equipment_type_entry_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_13, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_13, e), status=status.HTTP_400_BAD_REQUEST)
    
# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def update_equipment_type_entry(equipment_type_entry, request_data, fuel, user):
        try:
            db_name = user.db_access

            if not len(str(request_data.get("manufacturer"))) == 0 and request_data.get("manufacturer") is not None:
                manufacturer, manufacturer_response = ManufacturerHelper.get_manufacturer_by_name(request_data.get("manufacturer"), db_name)
                if manufacturer_response.status_code != status.HTTP_302_FOUND:
                    return equipment_type_entry, manufacturer_response
                equipment_type_entry.manufacturer = manufacturer
            if not len(str(request_data.get("asset_type"))) == 0 and request_data.get("asset_type") is not None:
                asset_type, asset_type_response = AssetTypeHelper.get_asset_type_by_name(request_data.get("asset_type"), db_name)
                if asset_type_response.status_code != status.HTTP_302_FOUND:
                    return equipment_type_entry, asset_type_response
                equipment_type_entry.asset_type = asset_type
            if not len(str(request_data.get("fuel_name"))) == 0 and request_data.get("fuel_name") is not None:
                equipment_type_entry.fuel = fuel
            if not len(str(request_data.get("model_number"))) == 0 and request_data.get("model_number") is not None:
                equipment_type_entry.model_number = request_data.get("model_number").strip()
            if not len(str(request_data.get("engine"))) == 0 and request_data.get("engine") is not None:
                equipment_type_entry.engine = request_data.get("engine").strip()
            if not len(str(request_data.get("fuel_tank_capacity"))) == 0 and request_data.get("fuel_tank_capacity") is not None:
                equipment_type_entry.fuel_tank_capacity = request_data.get("fuel_tank_capacity")
            if not len(str(request_data.get("fuel_tank_capacity_unit"))) == 0 and request_data.get("fuel_tank_capacity_unit") is not None:
                equipment_type_entry.fuel_tank_capacity_unit = request_data.get("fuel_tank_capacity_unit").strip()
                
            equipment_type_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            return equipment_type_entry, Response(status=status.HTTP_202_ACCEPTED)     

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_11, e))
            return equipment_type_entry, Response(CustomError.get_full_error_json(CustomError.TUF_11, e), status=status.HTTP_400_BAD_REQUEST)
   
# ---------------------------------------------------------------------------------------------------------------------
