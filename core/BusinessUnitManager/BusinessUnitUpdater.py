from rest_framework.response import Response
from rest_framework import status
from api.Models.business_unit import BusinessUnitModel
from ..LocationManager.LocationHelper import LocationHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class BusinessUnitUpdater():

    @staticmethod
    def create_business_unit_entry(business_unit_data, db_name):
        return BusinessUnitModel(
            name=business_unit_data.get("name").strip(),
            location=LocationHelper.get_location_by_name(business_unit_data.get("location").strip(), db_name),
            accounting_email=business_unit_data.get("accounting_email").strip()
        )