from rest_framework.response import Response
from rest_framework import status
from payment.Models.pricing_rates import PricingRates
from payment.Models.invoice_log import InvoiceLog
from payment.Models.pricing_rates import PricingRates
from GSE_Backend.errors.ErrorDictionary import CustomError

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class PaymentHelper():

    @staticmethod
    def get_all_pricing_rates():
        return PricingRates.objects.using('payment').all()

    @staticmethod
    def get_all_invoice_logs():
        return InvoiceLog.objects.using('payment').all()

    @staticmethod
    def get_invoice_logs_by_company_id(company_id):
        return InvoiceLog.objects.using('payment').filter(company_id=company_id)

    @staticmethod
    def get_pricing_rates_by_company_id(company_id):
        try:
            return PricingRates.objects.using('payment').get(company_id=company_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.RDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_invoice_log_by_id(invoice_log_id):
        try:
            return InvoiceLog.objects.using('payment').get(id=invoice_log_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.RDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def is_pricing_rate_currency_valid(currency_code):
        if currency_code in dict(PricingRates.currency_choices):
            return True
        return False

    @staticmethod
    def is_invoice_log_currency_valid(currency_code):
        if currency_code in dict(InvoiceLog.currency_choices):
            return True
        return False