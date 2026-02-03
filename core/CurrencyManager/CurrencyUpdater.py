from api.Models.Cost.currency import Currency
import logging 

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class CurrencyUpdater:

    @staticmethod
    def create_currency_entry(currency_data):
        return Currency(
            code=currency_data.get("code"),
            number=currency_data.get("number"),
            name=currency_data.get("name")
        )
