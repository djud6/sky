from rest_framework.response import Response
from rest_framework import status
from api.Models.inspection_type import InspectionTypeModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class InspectionTypeHelper():

    @staticmethod
    def get_all_inspection_types(db_name):
        return InspectionTypeModel.objects.using(db_name).all()

    @staticmethod
    def get_inspection_type_by_id(inspection_type_id, db_name):
        try:
            return InspectionTypeModel.objects.using(db_name).get(id=inspection_type_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ITDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ITDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_inspection_type_by_code(inspection_type_code, db_name):
        try:
            return InspectionTypeModel.objects.using(db_name).get(inspection_code=inspection_type_code), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ITDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ITDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def inspection_type_exists_by_code(inspection_type_code, db_name):
        return InspectionTypeModel.objects.using(db_name).filter(inspection_code=inspection_type_code).exists()