from rest_framework.response import Response
from rest_framework import status
from api.Models.Company import Company
from core.CurrencyManager.CurrencyHelper import CurrencyHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class CompanyUpdater():

    @staticmethod
    def create_company_entry(company_data, db_name):
        return Company(
            company_name=company_data.get("company_name"),
            company_address=company_data.get("company_address"),
            company_phone=company_data.get("company_phone"),
            standard_currency=CurrencyHelper.get_currency_by_code(company_data.get("standard_currency"), db_name),
            accounting_email=company_data.get("accounting_email"),
            software_logo=company_data.get("software_logo"),
            software_name=company_data.get("software_name")
        )