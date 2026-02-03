from rest_framework.response import Response
from rest_framework import status
from ..ChartCalculations.ChartCalculationsHelper import ChartCalculationsHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import requests
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class WebJobHelper():
    exchange_api_url = "http://api.exchangeratesapi.io/v1/latest?access_key=338f55416ed2470c8df6e7cf8ed2a044"
    backup_api_url = "https://openexchangerates.org/api/latest.json?app_id=ac4a72d610e14dc6a11beaceda0062bc"

    @staticmethod
    def get_currency_exchange_response():
        #base currency in api call is the EURO
        response = requests.get(WebJobHelper.exchange_api_url)

        #checking if the api call was successful
        if response.status_code != status.HTTP_200_OK:
            response = requests.get(WebJobHelper.backup_api_url)
        return response

    # Takes in list of managers and uses the user_location table to return subset of emails for the managers that
    # fit the location.
    @staticmethod
    def get_manager_emails_from_tuple_lists_for_location(manager_list, user_location_list, location_id):
        user_location_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, user_location_list, field_index=1)
        user_ids = [x[0] for x in user_location_subset]
        manager_subset = ChartCalculationsHelper.get_tpl_subset_in_field_list(user_ids, manager_list, field_index=0)
        return [x[1] for x in manager_subset]
