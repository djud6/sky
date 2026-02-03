from rest_framework.response import Response
from rest_framework import status
from api.Models.inspection_type import InspectionTypeModel
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class InspectionTypeUpdater():

    @staticmethod
    def create_inspection_type_entry(inspection_type_data):
        return InspectionTypeModel(
            inspection_name=inspection_type_data.get("inspection_name").strip(),
            inspection_code=inspection_type_data.get("inspection_code").strip(),
            required_at=inspection_type_data.get("required_at")
        )