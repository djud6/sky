from rest_framework.response import Response
from rest_framework import status
from api.Models.fleet_guru import FleetGuru
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class FleetGuruHelper():
    
    @staticmethod
    def get_fleet_guru_process(_process_name, db_name):
        return FleetGuru.objects.using(db_name).filter(process=_process_name)