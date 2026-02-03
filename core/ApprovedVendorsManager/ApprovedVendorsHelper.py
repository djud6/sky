from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from api.Models.asset_model import AssetModel
from api.Models.approved_vendors import ApprovedVendorsModel
from core.Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
import logging
import json

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ApprovedVendorsHelper():

    @staticmethod
    def select_related_to_approved_vendor(queryset):
        # return queryset.select_related(''
        return queryset

    @staticmethod
    def get_all_vendors(db_name):
        return ApprovedVendorsModel.objects.using(db_name).all()

    @staticmethod
    def get_vendor_by_id(vendor_id, db_name):
        try:
            return (
                ApprovedVendorsModel.objects.using(db_name).get(vendor_id=vendor_id),
                Response(status=status.HTTP_302_FOUND)
            )
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADNE_0, e))
            return (
                None,
                Response(
                    CustomError.get_full_error_json(CustomError.ADNE_0, e),
                    status=status.HTTP_400_BAD_REQUEST
                )
            )

    @staticmethod
    def get_vendor_by_name(vendor_name, db_name):
        try:
            return (
                ApprovedVendorsModel.objects.using(db_name).get(vendor_name=vendor_name),
                Response(status=status.HTTP_302_FOUND)
            )
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.VIDDNE_0, e))
            return (
                None,
                Response(
                    CustomError.get_full_error_json(CustomError.VIDDNE_0, e),
                    status=status.HTTP_400_BAD_REQUEST
                )
            )

    @staticmethod
    def get_vendors_by_id_list(id_list, db_name):
        return ApprovedVendorsModel.objects.using(db_name).filter(vendor_id__in=id_list)

    @staticmethod
    def get_vendors_by_service_type(service_type, db_name):
        if service_type == ApprovedVendorsModel.asset_request:
            return ApprovedVendorsModel.objects.using(db_name).filter(services_asset_request=True)
        elif service_type == ApprovedVendorsModel.maintenance:
            return ApprovedVendorsModel.objects.using(db_name).filter(services_maintenance=True)
        elif service_type == ApprovedVendorsModel.repair:
            return ApprovedVendorsModel.objects.using(db_name).filter(services_repair=True)
        elif service_type == ApprovedVendorsModel.disposal:
            return ApprovedVendorsModel.objects.using(db_name).filter(services_disposal=True)
        elif service_type == ApprovedVendorsModel.transfer:
            return ApprovedVendorsModel.objects.using(db_name).filter(services_transfer=True)
        return None

    @staticmethod
    def vendor_exists_by_name(vendor_name, db_name):
        return ApprovedVendorsModel.objects.using(db_name).filter(vendor_name=vendor_name).exists()

    @staticmethod
    def map_vendor_ids_to_names(db_name):
        '''
        Returns a dictionary with vendor_id as key and vendor_name as value.
        '''
        vendors = ApprovedVendorsModel.objects.using(db_name).all().values(
            "vendor_id",
            "vendor_name"
        )

        final_dict = {}
        for vendor in vendors:
            final_dict[str(vendor.get("vendor_id"))] = vendor.get("vendor_name")

        return final_dict

    @staticmethod
    def map_vendor_names_to_ids(db_name):
        '''
        Returns a dictionary with vendor_name as key and vendor_id as value.
        '''
        vendors = ApprovedVendorsModel.objects.using(db_name).all().values(
            "vendor_id",
            "vendor_name"
        )

        final_dict = {}
        for vendor in vendors:
            final_dict[str(vendor.get("vendor_name"))] = vendor.get("vendor_id")

        return final_dict

    @staticmethod
    def is_service_type_valid(service_type):
        if service_type in dict(ApprovedVendorsModel.service_type_choices):
            return True
        return False


    