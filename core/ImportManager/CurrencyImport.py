from rest_framework.response import Response
from rest_framework import status
from api.Models.Cost.currency import Currency
from ..CompanyManager.CompanyHelper import CompanyHelper
from ..CurrencyManager.CurrencyHelper import CurrencyHelper
from ..CurrencyManager.CurrencyUpdater import CurrencyUpdater
from api.Models.Snapshot.snapshot_daily_currency import SnapshotDailyCurrency
from ..SnapshotManager.SnapshotUpdater import SnapshotDailyCurrencyUpdater
from ..WebJobManager.WebJobHandler import WebJobHandler
from ..WebJobManager.WebJobHelper import WebJobHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class CurrencyImport():

    @staticmethod
    def import_currency_csv(parsed_data, db_name):
        try:
            #import currencies into Currency table
            currency_entries = []
            for currency_row in parsed_data:
                if not Currency.objects.using(db_name).filter(code=currency_row.get("code")).exists():
                    entry = CurrencyUpdater.create_currency_entry(currency_row)

                    currency_entries.append(entry)
            Currency.objects.using(db_name).bulk_create(currency_entries)

            #create the snapshot currency table
            standard_currency_id = CompanyHelper.get_list_companies(db_name)[0].standard_currency

            if (standard_currency_id == None):
                standard_currency = CurrencyHelper.get_currency_by_code("USD", db_name)
            else:
                standard_currency = CurrencyHelper.get_currency_by_id(standard_currency_id, db_name)

            currency_response = WebJobHelper.get_currency_exchange_response()
            
            if currency_response.status_code != status.HTTP_200_OK:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            #add currencies into snapshot table
            return SnapshotDailyCurrencyUpdater.update_snapshot_currencies(currency_response.json()['rates'], standard_currency.code, db_name)            
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_14, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_14, e), status=status.HTTP_400_BAD_REQUEST)