from rest_framework.response import Response
from rest_framework import status
from payment.Models.invoice_log import InvoiceLog

from payment.Models.pricing_rates import PricingRates
from ..Helper import HelperMethods
from .PaymentHelper import PaymentHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import numbers

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class PaymentUpdater():

    @staticmethod
    def create_pricing_rates_entry(request_data):
        return PricingRates(
            company_id = request_data.get('company_id'),
            rate_per_user = request_data.get('rate_per_user'),
            rate_per_asset = request_data.get('rate_per_asset'),
            data_overrage_fee = request_data.get('data_overrage_fee'),
            currency_code = request_data.get('currency_code')
        )

    @staticmethod
    def create_invoice_log_entry(request_data):
        return InvoiceLog(
            company_id = request_data.get('company_id'),
            total_billed_for_users = request_data.get('total_billed_for_users'),
            total_billed_for_assets = request_data.get('total_billed_for_assets'),
            total_billed_for_overrage_fees = request_data.get('total_billed_for_overrage_fees'),
            total_tax = request_data.get('total_tax'),
            currency_code = request_data.get('currency_code'),
            payment_due_date = request_data.get('payment_due_date')
        )

    @staticmethod
    def update_pricing_rates_fields(pricing_rates_entry, request_data):
        try:
            update_var = request_data.get("rate_per_user")
            if not len(str(update_var)) == 0 and update_var is not None and isinstance(update_var, numbers.Number):
                pricing_rates_entry.rate_per_user = update_var
            update_var = request_data.get("rate_per_asset")
            if not len(str(update_var)) == 0 and update_var is not None and isinstance(update_var, numbers.Number):
                pricing_rates_entry.rate_per_asset = update_var
            update_var = request_data.get("data_overrage_fee")
            if not len(str(update_var)) == 0 and update_var is not None and isinstance(update_var, numbers.Number):
                pricing_rates_entry.data_overrage_fee = update_var
            update_var = request_data.get("currency_code")
            if not len(str(update_var)) == 0 and update_var is not None and PaymentHelper.is_pricing_rate_currency_valid(update_var):
                pricing_rates_entry.currency_code = update_var

            return pricing_rates_entry, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_14, e))
            return pricing_rates_entry, Response(CustomError.get_full_error_json(CustomError.TUF_14, e), status=status.HTTP_400_BAD_REQUEST)