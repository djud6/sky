from rest_framework.response import Response
from rest_framework import status
from ..InspectionTypeManager.InspectionTypeUpdater import InspectionTypeUpdater
from api.Models.inspection_type import InspectionTypeModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class InspectionTypeImport():

    @staticmethod
    def import_inspection_type_csv(parsed_data, db_name):
        try:
            inspection_type_entries = []
            for inspection_type_row in parsed_data:
                if not InspectionTypeModel.objects.using(db_name).filter(inspection_code=inspection_type_row.get("inspection_code")).exists():
                    entry = InspectionTypeUpdater.create_inspection_type_entry(inspection_type_row)
                    inspection_type_entries.append(entry)
            InspectionTypeModel.objects.using(db_name).bulk_create(inspection_type_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_1, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_1, e), status=status.HTTP_400_BAD_REQUEST)