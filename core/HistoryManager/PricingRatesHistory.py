from rest_framework.response import Response
from rest_framework import status
from payment.Models.pricing_rates_history import PricingRatesHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class PricingRatesHistoryUpdater():

    @staticmethod
    def create_pricing_rates_record(pricing_rates_id, db_name):
        try:
            pricing_rates = PricingRatesHistoryUpdater.objects.using(db_name).get(id=pricing_rates_id)
            pricing_rates_history_entry = PricingRatesHistoryUpdater.generate_pricing_rates_history_entry(pricing_rates)
            pricing_rates_history_entry.save(using='payment')
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_pricing_rates_record_by_obj(pricing_rates):
        try:
            pricing_rates_history_entry = PricingRatesHistoryUpdater.generate_pricing_rates_history_entry(pricing_rates)
            pricing_rates_history_entry.save(using='payment')
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_pricing_rates_history_entry(pricing_rates):
        return PricingRatesHistory(
            pricing_rates=pricing_rates,
            company_id=pricing_rates.company_id,
            rate_per_user=pricing_rates.rate_per_user,
            rate_per_asset=pricing_rates.rate_per_asset,
            data_overrage_fee=pricing_rates.data_overrage_fee,
            currency_code=pricing_rates.currency_code
        )