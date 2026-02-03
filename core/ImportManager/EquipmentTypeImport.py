from rest_framework.response import Response
from rest_framework import status
from ..EquipmentTypeManager.EquipmentTypeUpdater import EquipmentTypeUpdater
from ..EquipmentTypeManager.EquipmentTypeHelper import EquipmentTypeHelper
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from ..ManufacturerManager.ManufacturerHelper import ManufacturerHelper
from api.Models.equipment_type import EquipmentTypeModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class EquipmentTypeImport():

    @staticmethod
    def import_equipment_type_csv(parsed_data, user):
        try:
            equipment_type_entries = []
            for equipment_type_row in parsed_data:
                manufacturer_id = ManufacturerHelper.get_manufacturer_id_by_name(equipment_type_row.get("manufacturer"), user.db_access)
                model_number = equipment_type_row.get("model_number").strip()
                if not EquipmentTypeModel.objects.using(user.db_access).filter(manufacturer=manufacturer_id).filter(model_number=model_number).exists():
                    entry, entry_response = EquipmentTypeUpdater.create_equipment_type_entry(equipment_type_row, user)
                    if entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return entry_response
                    equipment_type_entries.append(entry)
            EquipmentTypeModel.objects.using(user.db_access).bulk_create(equipment_type_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_2, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_2, e), status=status.HTTP_400_BAD_REQUEST)