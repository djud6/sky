import statistics
from rest_framework.response import Response
from rest_framework import status
from api.Models.request_quote import RequestQuote
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RequestQuoteUpdater():

    @staticmethod
    def update_quote_fields(quote_entry, request_data):
        try:
            if not len(str(request_data.get("status"))) == 0 and request_data.get("status") is not None:
                quote_entry.status = request_data.get("status")
            if not len(str(request_data.get("vendor_quote_id"))) == 0 and request_data.get("vendor_quote_id") is not None:
                quote_entry.vendor_quote_id = request_data.get("vendor_quote_id")
            if not len(str(request_data.get("estimated_cost"))) == 0 and request_data.get("estimated_cost") is not None:
                quote_entry.estimated_cost = request_data.get("estimated_cost")     
                
            return quote_entry, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_15, e))
            return quote_entry, Response(CustomError.get_full_error_json(CustomError.TUF_15, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def status_bulk_update(quote_ids, status, db_name):
        RequestQuote.objects.using(db_name).filter(id__in=quote_ids).update(status=status)