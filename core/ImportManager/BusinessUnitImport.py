from rest_framework.response import Response
from rest_framework import status
from ..BusinessUnitManager.BusinessUnitUpdater import BusinessUnitUpdater
from api.Models.business_unit import BusinessUnitModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class BusinessUnitImport():

    @staticmethod
    def import_business_unit_csv(parsed_data, db_name):
        try:
            business_unit_entries = []
            for business_unit_row in parsed_data:
                if not BusinessUnitModel.objects.using(db_name).filter(name=business_unit_row.get("name")).exists():
                    entry = BusinessUnitUpdater.create_business_unit_entry(business_unit_row, db_name)
                    business_unit_entries.append(entry)
            BusinessUnitModel.objects.using(db_name).bulk_create(business_unit_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_5, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_5, e), status=status.HTTP_400_BAD_REQUEST)