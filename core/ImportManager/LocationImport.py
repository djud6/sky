from rest_framework.response import Response
from rest_framework import status
from ..LocationManager.LocationUpdater import LocationUpdater
from api.Models.locations import LocationModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class LocationImport():

    @staticmethod
    def import_location_csv(parsed_data, db_name):
        try:
            location_entries = []
            for location_row in parsed_data:
                if not LocationModel.objects.using(db_name).filter(location_name=location_row.get("location_name")).exists():
                    entry = LocationUpdater.create_location_entry(location_row)
                    location_entries.append(entry)
            LocationModel.objects.using(db_name).bulk_create(location_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_1, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_1, e), status=status.HTTP_400_BAD_REQUEST)