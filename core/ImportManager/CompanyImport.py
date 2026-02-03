from rest_framework.response import Response
from rest_framework import status
from ..CompanyManager.CompanyUpdater import CompanyUpdater
from api.Models.Company import Company
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class CompanyImport():

    @staticmethod
    def import_company_csv(parsed_data, db_name):
        try:
            company_entries = []
            for company_row in parsed_data:
                if not Company.objects.using(db_name).filter(company_name=company_row.get("company_name")).exists():
                    entry = CompanyUpdater.create_company_entry(company_row, db_name)
                    company_entries.append(entry)
            Company.objects.using(db_name).bulk_create(company_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_10, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_10, e), status=status.HTTP_400_BAD_REQUEST)