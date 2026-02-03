from rest_framework.response import Response
from rest_framework import status
from api.Models.approved_vendors import ApprovedVendorsModel
from .ApprovedVendorsHelper import ApprovedVendorsHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ApprovedVendorsUpdater():

    @staticmethod
    def create_approved_vendor_entry(approved_vendor_data, db_name):
        return ApprovedVendorsModel(
            vendor_name=approved_vendor_data.get("vendor_name").strip(),
            is_vendor_green=approved_vendor_data.get("is_vendor_green"),
            phone_number = approved_vendor_data.get("phone_number"),
            address = approved_vendor_data.get("address"),
            website = approved_vendor_data.get("website"),
            primary_email = approved_vendor_data.get("primary_email"),
            rating = approved_vendor_data.get("rating"),
            services_asset_request = approved_vendor_data.get("services_asset_request"),
            services_maintenance = approved_vendor_data.get("services_maintenance"),
            services_repair = approved_vendor_data.get("services_repair"),
            services_disposal = approved_vendor_data.get("services_disposal"),
            services_transfer = approved_vendor_data.get("services_transfer")
        )

    @staticmethod
    def update_vendor_services(vendor_name, service_config, db_name):
        '''
        expecting task_config to be a dict/json with every task as key and a bool value
        '''
        ApprovedVendorsModel.objects.using(db_name).filter(
            vendor_name=vendor_name
            ).update(
                services_asset_request = service_config.get("asset request"),
                services_maintenance = service_config.get("maintenance"),
                services_repair = service_config.get("repair"),
                services_disposal = service_config.get("disposal"),
                services_transfer = service_config.get("transfer")
            )