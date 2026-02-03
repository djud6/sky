from rest_framework.response import Response
from rest_framework import status
from api.Models.equipment_type import EquipmentTypeModel
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class EquipmentTypeHelper():
    
    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_equipment_type_by_asset_type_id_and_manufacturer(asset_id, manufacturer_id, db_name):
        try:
            return EquipmentTypeModel.objects.using(db_name).filter(asset_type__id=asset_id, manufacturer__id=manufacturer_id), Response(status=status.HTTP_302_FOUND)
        except EquipmentTypeModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.EDNE_0))
            return None, Response(CustomError.get_full_error_json(CustomError.EDNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def select_related_to_equipment_type(queryset):
        return queryset.select_related('manufacturer', 'asset_type', 'fuel')

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_all_equipment_types(db_name):
        try:
            return EquipmentTypeModel.objects.using(db_name).all(), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.EDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.EDNE_0, e), status=status.HTTP_400_BAD_REQUEST)    

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_equipment_type_by_id(equipment_type_id, db_name):
        try:
            return EquipmentTypeModel.objects.using(db_name).get(equipment_type_id=equipment_type_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.EDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.EDNE_0, e), status=status.HTTP_400_BAD_REQUEST)    

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_equipment_type_id_by_asset_type(asset_type, db_name):
        return EquipmentTypeModel.objects.using(db_name).filter(asset_type=asset_type).value_list('equipment_type_id', flat=True)[0]

    # --------------------------------------------------------------------------------------

    @staticmethod
    def get_equipment_type_by_model_and_manufacturer(model, manufacturer_id, db_name):
        return EquipmentTypeModel.objects.using(db_name).get(model_number=model, manufacturer=manufacturer_id)
    # --------------------------------------------------------------------------------------

    @staticmethod
    def equipment_type_by_model_and_manufacturer_exists(model, manufacturer_id, db_name):
        return EquipmentTypeModel.objects.using(db_name).filter(model_number=model, manufacturer=manufacturer_id).exists()
    # --------------------------------------------------------------------------------------

    @staticmethod
    def equipment_type_by_model_manufacturer_engine_fuel_exists(model, manufacturer_id, asset_type_id, engine, fuel_id, db_name):
        return EquipmentTypeModel.objects.using(db_name).filter(model_number=model, manufacturer=manufacturer_id, asset_type=asset_type_id, engine=engine, fuel=fuel_id).exists()
    # --------------------------------------------------------------------------------------

    @staticmethod
    def model_number_check(request_data, equipment_type_obj):
        if request_data.get("model_number") is not None:
            model_number = request_data.get("model_number")
        else:
            model_number = equipment_type_obj.model_number
        return model_number
    # --------------------------------------------------------------------------------------

    @staticmethod
    def engine_check(request_data, equipment_type_obj):
        if request_data.get("engine") is not None:
            engine = request_data.get("engine")

        elif equipment_type_obj.engine is not None:
            engine = equipment_type_obj.engine
        else:
            engine = 'V6'
        return engine
    # --------------------------------------------------------------------------------------
