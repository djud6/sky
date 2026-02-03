from rest_framework.response import Response
from rest_framework import status
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class FleetGuruUpdater():
    pass