from rest_framework.response import Response
from rest_framework import status
from api.Models.locations import LocationModel
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class LocationUpdater():

    @staticmethod
    def create_location_entry(location_data):
        return LocationModel(
            location_code=location_data.get("location_code").strip(),
            location_name=location_data.get("location_name").strip(),
            longitude=location_data.get("longitude"),
            latitude=location_data.get("latitude")
        )