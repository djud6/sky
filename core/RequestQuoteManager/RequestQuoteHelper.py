import statistics
from urllib.parse import quote_plus
from rest_framework.response import Response
from rest_framework import status

from core.ApprovedVendorsManager.ApprovedVendorsHelper import ApprovedVendorsHelper
from ..VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from api.Models.request_quote import RequestQuote
import itertools
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RequestQuoteHelper():

    @staticmethod
    def parse_batch_quote_input(request_data, request_type):
        '''
        Meant to be used to parse quote data for multiple requests.
        '''
        data_lists = []
        for request in request_data:
            data_lists.append(
                RequestQuoteHelper.parse_quote_input(
                    request.get("potential_vendor_ids"),
                    request.get("request_id"),
                    request_type
                )
            )
        return list(itertools.chain.from_iterable(data_lists))

    @staticmethod
    def parse_quote_input(potential_vendors, request_id, request_type):
        '''
        Meant to be used to parse quote data for one request.
        '''
        request_quote_data = []
        potential_vendors_list = potential_vendors[1:][:-1].split("-")
        for vendor_id in potential_vendors_list:
            entry = None
            entry = {
                "vendor": vendor_id,
                request_type: request_id
            }
            request_quote_data.append(entry)
        return request_quote_data


    @staticmethod
    def generate_vendor_quote_input(requests, client_company_name, db_name):
        '''
        This method generates the input required by the vendor enpoints
        which bulk create vendor side quote entries for asset request,
        maintenance, repair, and disposal.
        '''

        vendor_companies = list(VendorOpsHelper.get_all_vendor_companies().values(
                "company_name",
            )
        )

        vendor_id_name_mapping = ApprovedVendorsHelper.map_vendor_ids_to_names(db_name)

        vendor_quote_data = []
        for vendor_company in vendor_companies:
            cur_ven_quote_data = {
                "vendor_name": vendor_company.get("company_name"),
                "client_company_name": client_company_name
            }
            request_ids = []
            for request in requests:
                potential_vendor_ids = request.get("potential_vendor_ids")
                if potential_vendor_ids:
                    potential_vendors_id_list = potential_vendor_ids[1:][:-1].split("-")
                    for vendor_id in potential_vendors_id_list:
                        if vendor_id_name_mapping.get(vendor_id) == vendor_company.get("company_name"):
                            request_ids.append(request.get("request_custom_id"))
            cur_ven_quote_data["request_ids"] = request_ids
            if len(request_ids) > 0:
                vendor_quote_data.append(cur_ven_quote_data)

        return vendor_quote_data

    # ------------------------------------------------------------------------------

    @staticmethod
    def get_all_request_quotes(db_name):
        return RequestQuote.objects.using(db_name).all()

    @staticmethod
    def get_all_asset_request_quotes(db_name):
        return RequestQuote.objects.using(db_name).exclude(asset_request=None)

    @staticmethod
    def get_all_maintenance_quotes(db_name):
        return RequestQuote.objects.using(db_name).exclude(maintenance_request=None)

    @staticmethod
    def get_all_repair_quotes(db_name):
        return RequestQuote.objects.using(db_name).exclude(repair_request=None)

    @staticmethod
    def get_all_disposal_quotes(db_name):
        return RequestQuote.objects.using(db_name).exclude(disposal_request=None)

    @staticmethod
    def get_all_transfer_quotes(db_name):
        return RequestQuote.objects.using(db_name).exclude(transfer_request=None)

    @staticmethod
    def get_all_asset_request_quotes_by_vendor_name(vendor_name, db_name):
        return RequestQuote.objects.using(db_name).filter(
            vendor__vendor_name=vendor_name
        ).exclude(
            asset_request=None
        )

    @staticmethod
    def get_all_maintenance_quotes_by_vendor_name(vendor_name, db_name):
        return RequestQuote.objects.using(db_name).filter(
            vendor__vendor_name=vendor_name
        ).exclude(
            maintenance_request=None
        )

    @staticmethod
    def get_all_repair_quotes_by_vendor_name(vendor_name, db_name):
        return RequestQuote.objects.using(db_name).filter(
            vendor__vendor_name=vendor_name
        ).exclude(
            repair_request=None
        )

    @staticmethod
    def get_all_disposal_quotes_by_vendor_name(vendor_name, db_name):
        return RequestQuote.objects.using(db_name).filter(
            vendor__vendor_name=vendor_name
        ).exclude(
            disposal_request=None
        )

    @staticmethod
    def get_all_transfer_quotes_by_vendor_name(vendor_name, db_name):
        return RequestQuote.objects.using(db_name).filter(
            vendor__vendor_name=vendor_name
        ).exclude(
            transfer_request=None
        )

    @staticmethod
    def get_request_quote_by_id(quote_id, db_name):
        try:
            return RequestQuote.objects.using(db_name).get(id=quote_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RQDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.RQDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_request_quotes_by_id_list(id_list, db_name):
        return RequestQuote.objects.using(db_name).filter(id__in=id_list)

    @staticmethod
    def get_quote_by_request_custom_id_and_vendor_name(custom_id, vendor_name, db_name):
        type = custom_id.split("-")[1]
        if type == "ar":
            return RequestQuote.objects.using(db_name).get(
                asset_request__custom_id=custom_id,
                vendor__vendor_name=vendor_name
            )
        elif type == "m":
            return RequestQuote.objects.using(db_name).get(
                maintenance_request__work_order=custom_id,
                vendor__vendor_name=vendor_name
            )
        elif type == "r":
            return RequestQuote.objects.using(db_name).get(
                repair_request__work_order=custom_id,
                vendor__vendor_name=vendor_name
            )
        elif type == "d":
            return RequestQuote.objects.using(db_name).get(
                disposal_request__custom_id=custom_id,
                vendor__vendor_name=vendor_name
            )
        elif type == "t":
            return RequestQuote.objects.using(db_name).get(
                transfer_request__custom_id=custom_id,
                vendor__vendor_name=vendor_name
            )
        else:
            return None

    @staticmethod
    def get_expired_quotes(expiry_date, db_name):
        return RequestQuote.objects.using(db_name).filter(
            status=RequestQuote.pending,
            date_created__lt=expiry_date
        )

    @staticmethod
    def get_quotes_by_daterange(start, end, db_name):
        return RequestQuote.objects.using(db_name).filter(date_created__range=[start, end])

    @staticmethod
    def get_unapproved_asset_request_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            asset_request=request_id
        ).exclude(
            status=RequestQuote.shortlisted
        )
    
    @staticmethod
    def get_asset_request_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            asset_request=request_id
        )

    @staticmethod
    def get_unapproved_maintenance_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            maintenance_request=request_id
        ).exclude(
            status=RequestQuote.shortlisted
        )
    
    @staticmethod
    def get_maintenance_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            maintenance_request=request_id
        )

    @staticmethod
    def get_unapproved_repair_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            repair_request=request_id
        ).exclude(
            status=RequestQuote.shortlisted
        )

    @staticmethod
    def get_repair_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            repair_request=request_id
        )

    @staticmethod
    def get_unapproved_disposal_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            disposal_request=request_id
        ).exclude(
            status=RequestQuote.shortlisted
        )

    @staticmethod
    def get_disposal_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            disposal_request=request_id
        )

    @staticmethod
    def get_unapproved_disposal_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            disposal_request=request_id
        ).exclude(
            status=RequestQuote.shortlisted
        )

    @staticmethod
    def get_transfer_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            transfer_request=request_id
        )

    @staticmethod
    def get_unapproved_transfer_quotes_by_request_id(request_id, db_name):
        return RequestQuote.objects.using(db_name).filter(
            transfer_request=request_id
        ).exclude(
            status=RequestQuote.shortlisted
        )

    # ------------------------------------------------------------------------------

    @staticmethod
    def filter_rejected_quotes(data):
        '''
        To be used for serializer.data of Repair, Maintenance
        Asset Request, Transfer, and Disposal when queried by a vendor.
        Will filter out process entries that have been rejected
        by the vendor that is making the query.
        '''
        filtered_data = []
        for request in data:
            quotes = request.get("quotes")
            if len(quotes) > 0:
                if quotes[0].get("status") != RequestQuote.denied:
                    filtered_data.append(request)
            else:
                filtered_data.append(request)
        return filtered_data

    @staticmethod
    def get_request_info_quote_obj(quote_obj):
        '''
        Gets request id, custom id, VIN, and request type
        from quote object.
        '''
        if quote_obj.asset_request is not None:
            return (
                quote_obj.asset_request.id,
                quote_obj.asset_request.custom_id,
                quote_obj.asset_request.VIN,
                "asset request"
            )
        elif quote_obj.maintenance_request is not None:
            return (
                quote_obj.maintenance_request.maintenance_id,
                quote_obj.maintenance_request.work_order,
                quote_obj.maintenance_request.VIN,
                "maintenance"
            )
        elif quote_obj.repair_request is not None:
            return (
                quote_obj.repair_request.repair_id,
                quote_obj.repair_request.work_order,
                quote_obj.repair_request.VIN,
                "repair"
            )
        elif quote_obj.disposal_request is not None:
            return (
                quote_obj.disposal_request.id,
                quote_obj.disposal_request.custom_id,
                quote_obj.disposal_request.VIN,
                "disposal"
            )
        elif quote_obj.transfer_request is not None:
            return (
                quote_obj.transfer_request.asset_transfer_id,
                quote_obj.transfer_request.custom_id,
                quote_obj.transfer_request.VIN,
                "transfer"
            )

    # ------------------------------------------------------------------------------




