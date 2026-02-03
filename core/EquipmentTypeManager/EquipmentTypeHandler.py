from rest_framework.response import Response
from rest_framework import status
from ..EquipmentTypeManager.EquipmentTypeUpdater import EquipmentTypeUpdater
from ..EquipmentTypeManager.EquipmentTypeHelper import EquipmentTypeHelper
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from ..ManufacturerManager.ManufacturerHelper import ManufacturerHelper
from ..ManufacturerManager.ManufacturerUpdater import ManufacturerUpdater
from ..AssetTypeManager.AssetTypeUpdater import AssetTypeUpdater
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from ..CostManager.CostUpdater import FuelUpdater
from ..CostManager.CostHelper import FuelHelper
from api.Models.asset_type import AssetTypeModel
from api.Models.equipment_type import EquipmentTypeModel
from api.Serializers.serializers import EquipmentTypeSerializer, LightEquipmentTypeSerializer
from api.Models.asset_manufacturer import AssetManufacturerModel
from api.Models.fuel_type import FuelType
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class EquipmentTypeHandler():

    @staticmethod
    def handle_add_equipment_type(request_data, user):
        try:
            db_name = user.db_access

            if not request_data.get("manufacturer") or not request_data.get("asset_type") or not request_data.get("model_number"):
                Logger.getLogger().error(CustomError.RFNP_0)
                return Response(CustomError.get_full_error_json(CustomError.RFNP_0), status=status.HTTP_400_BAD_REQUEST)
            if not ManufacturerHelper.manufacturer_exists(request_data.get("manufacturer"), db_name):
                if not len(str(request_data.get("manufacturer"))) == 0 and request_data.get("manufacturer") is not None:
                    manufacturer_entry, manufacturer_entry_response = ManufacturerUpdater.create_manufacturer_entry(request_data, user)
                    if manufacturer_entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return manufacturer_entry_response
                    manufacturer_entry.save()
                    manufacturer_id = manufacturer_entry.id
            else:
                manufacturer_id = ManufacturerHelper.get_manufacturer_id_by_name(request_data.get("manufacturer"), db_name)

            if not AssetTypeHelper.asset_type_exists_by_name(request_data.get("asset_type"), db_name):
                if not len(str(request_data.get("asset_type"))) == 0 and request_data.get("asset_type") is not None:
                    asset_type_entry, asset_type_entry_response = AssetTypeUpdater.create_asset_type_entry(request_data, user)
                    if asset_type_entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return asset_type_entry_response
                    asset_type_entry.save()

            if not FuelHelper.fuel_type_exists(request_data.get("fuel_name"), db_name):
                if not len(str(request_data.get("fuel_name"))) == 0 and request_data.get("fuel_name") is not None:
                    fuel_type_entry, fuel_type_entry_response = FuelUpdater.create_fuel_type_entry(request_data, user)
                    if fuel_type_entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return fuel_type_entry_response
                    fuel_type_entry.save()

            if not EquipmentTypeHelper.equipment_type_by_model_and_manufacturer_exists(request_data.get("model_number"), manufacturer_id, db_name):
                equipment_type_entry, equipment_type_entry_response = EquipmentTypeUpdater.create_equipment_type_entry(request_data, user)
                if equipment_type_entry_response.status_code != status.HTTP_202_ACCEPTED:
                    return equipment_type_entry_response
                equipment_type_entry.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.ETEAE_0)
                return Response(CustomError.get_full_error_json(CustomError.ETEAE_0), status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------


    @staticmethod
    def handle_get_all_equipment_types(user):
        try:
            queryset, queryset_response = EquipmentTypeHelper.get_all_equipment_types(user.db_access)
            if queryset_response.status_code != status.HTTP_302_FOUND:
                return queryset_response
            relevant_qs = EquipmentTypeHelper.select_related_to_equipment_type(queryset)
            ser = LightEquipmentTypeSerializer(relevant_qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_equipment_type(request_data, user):
        try:
            db_name = user.db_access

            if not request_data.get("equipment_type_id"):
                Logger.getLogger().error(CustomError.RFNP_1)
                return Response(CustomError.get_full_error_json(CustomError.RFNP_1), status=status.HTTP_400_BAD_REQUEST)

            if not len(str(request_data.get("equipment_type_id"))) == 0 and request_data.get("equipment_type_id") is not None:
                equipment_type_obj, equipment_type_response = EquipmentTypeHelper.get_equipment_type_by_id(request_data.get("equipment_type_id"), user.db_access)
                if equipment_type_response.status_code != status.HTTP_302_FOUND:
                    return equipment_type_response

            if not len(str(request_data.get("manufacturer"))) == 0 and request_data.get("manufacturer") is not None:
                if not ManufacturerHelper.manufacturer_exists(request_data.get("manufacturer"), db_name):
                    manufacturer_entry, manufacturer_entry_response = ManufacturerUpdater.create_manufacturer_entry(request_data, user)
                    if manufacturer_entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return manufacturer_entry_response
                    manufacturer_entry.save()
                    manufacturer_id = manufacturer_entry.id
                else:
                    manufacturer_id = ManufacturerHelper.get_manufacturer_id_by_name(request_data.get("manufacturer"), db_name)
            
            else:
                manufacturer_id = ManufacturerHelper.get_manufacturer_id_by_name(equipment_type_obj.manufacturer, db_name)

            if not len(str(request_data.get("asset_type"))) == 0 and request_data.get("asset_type") is not None:
                if not AssetTypeHelper.asset_type_exists_by_name(request_data.get("asset_type"), db_name):
                    asset_type_entry, asset_type_entry_response = AssetTypeUpdater.create_asset_type_entry(request_data, user)
                    if asset_type_entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return asset_type_entry_response
                    asset_type_entry.save()
                    asset_type_id = asset_type_entry.id
                else:
                    asset_type_id = AssetTypeHelper.get_asset_type_id_by_name(request_data.get("asset_type"), db_name)
            else:
                asset_type_id = AssetTypeHelper.get_asset_type_id_by_name(equipment_type_obj.asset_type, db_name)

            if not len(str(request_data.get("fuel_name"))) == 0 and request_data.get("fuel_name") is not None:
                if not FuelHelper.fuel_type_exists(request_data.get("fuel_name"), db_name):
                    fuel_type_entry, fuel_type_entry_response = FuelUpdater.create_fuel_type_entry(request_data, user)
                    if fuel_type_entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return fuel_type_entry_response
                    fuel_type_entry.save()
                    fuel = fuel_type_entry
                    fuel_id = fuel_type_entry.id
                else:
                    fuel, fuel_type_response = FuelHelper.get_fuel_type_by_name(request_data.get("fuel_name"), db_name)
                    fuel_id = fuel.id
            elif equipment_type_obj.fuel is not None:
                fuel = request_data.get("fuel_name")
                fuel_id = equipment_type_obj.fuel.id
            else:
                fuel = request_data.get("fuel_name")
                fuel_id = 1
                
            model_number = EquipmentTypeHelper.model_number_check(request_data, equipment_type_obj)
            engine = EquipmentTypeHelper.engine_check(request_data, equipment_type_obj)
            
            if not EquipmentTypeHelper.equipment_type_by_model_manufacturer_engine_fuel_exists(model_number, manufacturer_id, asset_type_id, engine, fuel_id, db_name):
                equipment_type_entry, equipment_type_entry_response = EquipmentTypeUpdater.update_equipment_type_entry(equipment_type_obj, request_data, fuel, user)
                if equipment_type_entry_response.status_code != status.HTTP_202_ACCEPTED:
                    return equipment_type_entry_response
                equipment_type_entry.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                Logger.getLogger().error(CustomError.ETEAE_0)
                return Response(CustomError.get_full_error_json(CustomError.ETEAE_0), status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
