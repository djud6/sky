from rest_framework.response import Response
from rest_framework import status
from ..CostManager.CostUpdater import FuelUpdater
from api.Models.fuel_type import FuelType
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class FuelTypeImport():

    @staticmethod
    def import_fuel_type_csv(parsed_data, user):
        try:
            db_name = user.db_access
            fuel_type_entries = []
            for fuel_type_row in parsed_data:
                if not FuelType.objects.using(db_name).filter(name=fuel_type_row.get("name")).exists():
                    entry, entry_response = FuelUpdater.create_fuel_type_entry(fuel_type_row, user)
                    if entry_response.status_code != status.HTTP_202_ACCEPTED:
                        return entry_response
                    fuel_type_entries.append(entry)
            FuelType.objects.using(db_name).bulk_create(fuel_type_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_6, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_6, e), status=status.HTTP_400_BAD_REQUEST)