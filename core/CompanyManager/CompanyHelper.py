from rest_framework.response import Response
from rest_framework import status
from api.Models.Company import Company
from api.Models.Cost.currency import Currency
from django.core.exceptions import ObjectDoesNotExist
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class CompanyHelper():

    @staticmethod
    def get_company_by_name(company_name, db_name):
        try:
            return Company.objects.using(db_name).get(company_name=company_name), Response(status=status.HTTP_302_FOUND)
        except Company.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CDNE_0))
            return None, Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_company_by_id(company_id, db_name):
        try:
            return Company.objects.using(db_name).get(company_id=company_id), Response(status=status.HTTP_302_FOUND)
        except Company.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CDNE_0))
            return None, Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_company_id_by_name(company_name, db_name):
        return Company.objects.using(db_name).filter(company_name=company_name).values_list('company_id', flat=True)[0]

    @staticmethod
    def get_list_companies(db_name):
        return Company.objects.using(db_name).all()

    @staticmethod
    def get_standard_currency_by_company_obj(company_obj, db_name):
        if company_obj.standard_currency is None:
            return Currency.objects.using(db_name).get(code='USD')
        return company_obj.standard_currency

    @staticmethod
    def get_standard_currency_code_by_company_obj(company_obj, db_name):
        standard_currency = CompanyHelper.get_standard_currency_by_company_obj(company_obj, db_name)
        if standard_currency is not None:
            return standard_currency.code
        else:
            return None