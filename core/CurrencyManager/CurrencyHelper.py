from rest_framework.response import Response
from rest_framework import status
from api.Models.Cost.currency import Currency
from ..UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class CurrencyHelper():

    @staticmethod
    def get_currency_by_name(currency_name, db_name):
        return Currency.objects.using(db_name).get(name=currency_name)

    @staticmethod
    def get_currency_by_id(currency_id, db_name):
        return Currency.objects.using(db_name).get(id=currency_id)

    @staticmethod
    def get_currency_by_code(currency_code, db_name):
        return Currency.objects.using(db_name).get(code=currency_code)
    
    @staticmethod
    def get_list_currencies(db_name):
        return Currency.objects.using(db_name).all()