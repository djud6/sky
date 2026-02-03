from xmlrpc.client import DateTime
from django.utils import timezone
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
import core.AssetRequestManager as AssetRequestManager
from core.AssetRequestManager.AssetRequestHelper import AssetRequestHelper
import core.MaintenanceManager as MaintenanceManager
import core.DisposalManager as DisposalManager
import core.RepairManager as RepairManager
import core.TransferManager as TransferManager
from api.Models.request_quote import RequestQuote
from api.Models.asset_request import AssetRequestModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.repairs import RepairsModel
from api.Models.asset_transfer import AssetTransfer
from api.Models.asset_disposal import AssetDisposalModel
from api.Serializers.serializers import RequestQuoteSerializer
from core.UserManager.UserHelper import UserHelper
from .RequestQuoteHelper import RequestQuoteHelper
from .RequestQuoteUpdater import RequestQuoteUpdater
from ..VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import json
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RequestQuoteHandler():

    @staticmethod
    def handle_create_batch_quotes(request_data):
        try:
            ser = RequestQuoteSerializer(data=request_data, many=True)
            if ser.is_valid():
                ser.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)  

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_quote(request_data, user):
        try:
            quote = RequestQuoteHelper.get_quote_by_request_custom_id_and_vendor_name(
                request_data.get("request_custom_id"),
                request_data.get("vendor_name"),
                user.db_access
            )

            updated_quote, update_response = RequestQuoteUpdater.update_quote_fields(quote, request_data)
            if update_response.status_code != status.HTTP_202_ACCEPTED:
                return update_response
                
            updated_quote.save(using=user.db_access)

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_list_request_quotes(user):
        try:
            qs = RequestQuoteHelper.get_all_request_quotes(user.db_access)
            ser = RequestQuoteSerializer(qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_approve_quote(quote_id, user):
        try:
            # Change selected quote to accepted
            shortlisted_quote, resp = RequestQuoteHelper.get_request_quote_by_id(quote_id, user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
                
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
            shortlisted_quote.status = RequestQuote.shortlisted
            shortlisted_quote.approved_by = detailed_user
            shortlisted_quote.save()

            # Get request id and type
            request_id, custom_id, vin, request_type = RequestQuoteHelper.get_request_info_quote_obj(
                shortlisted_quote
            )

            # Change all other quotes for this request to denied
            # Make associated request to awaiting approval status
            # Or auto-approve them if the creating user has the allowance
            rejected_quotes = None
            update_resp = None
            if request_type == "asset request":
                rejected_quotes = RequestQuoteHelper.get_unapproved_asset_request_quotes_by_request_id(
                    request_id,
                    user.db_access
                )

                update_resp = AssetRequestManager.AssetRequestHandler.AssetRequestHandler.handle_update_asset_request(
                    {
                        "estimated_cost": shortlisted_quote.estimated_cost,
                        "asset_request_id": request_id,
                        "chosen_vendor_obj": shortlisted_quote.vendor
                    },
                    user
                )
                if update_resp.status_code != status.HTTP_202_ACCEPTED:
                    return update_resp
                    
            elif request_type == "maintenance":
                rejected_quotes = RequestQuoteHelper.get_unapproved_maintenance_quotes_by_request_id(
                    request_id,
                    user.db_access
                )
                update_resp = MaintenanceManager.MaintenanceHandler.MaintenanceHandler.handle_update_maintenance(
                    {
                        "estimated_cost": shortlisted_quote.estimated_cost,
                        "maintenance_id": request_id,
                        "chosen_vendor_obj": shortlisted_quote.vendor
                    },
                    user
                )

            elif request_type == "repair":
                rejected_quotes = RequestQuoteHelper.get_unapproved_repair_quotes_by_request_id(
                    request_id,
                    user.db_access
                )
                update_resp = RepairManager.RepairHandler.RepairHandler.handle_update_repair(
                    {
                        "estimated_cost": shortlisted_quote.estimated_cost,
                        "repair_id": request_id,
                        "chosen_vendor_obj": shortlisted_quote.vendor
                    },
                    user
                )

            elif request_type == "disposal":
                rejected_quotes = RequestQuoteHelper.get_unapproved_disposal_quotes_by_request_id(
                    request_id,
                    user.db_access
                )
                update_resp = DisposalManager.DisposalHandler.DisposalHandler.handle_update_disposal(
                    {
                        "estimated_cost": shortlisted_quote.estimated_cost,
                        "disposal_id": request_id,
                        "chosen_vendor_obj": shortlisted_quote.vendor
                    },
                    user,
                )

            elif request_type == "transfer":
                rejected_quotes = RequestQuoteHelper.get_unapproved_transfer_quotes_by_request_id(
                    request_id,
                    user.db_access
                )
                update_resp = TransferManager.TransferHandler.TransferHandler.handle_update_transfer(
                    {
                        "estimated_cost": shortlisted_quote.estimated_cost,
                        "transfer_id": request_id,
                        "chosen_vendor_obj": shortlisted_quote.vendor
                    },
                    user,
                )

            # Check if status update was successful
            if update_resp.status_code != status.HTTP_202_ACCEPTED:
                return update_resp

            if rejected_quotes:
                rejected_quotes.update(status=RequestQuote.denied)

            vendor_company_info = VendorOpsHelper.get_all_vendor_companies().values(
                "company_name",
            )

            rejected_vendor_names_list = list(rejected_quotes.values_list(
                "vendor__vendor_name",
                flat=True
            ))

            # Add all vendors who have been denied and shortlisted to be updated on vendor side
            vendor_quote_statuses = []
            for company in vendor_company_info:
                if company.get("company_name") in rejected_vendor_names_list:
                    vendor_quote_statuses.append(
                        {
                            "vendor_name": company.get("company_name"),
                            "status": RequestQuote.denied
                        }
                    )
                elif company.get("company_name") == shortlisted_quote.vendor.vendor_name:
                    vendor_quote_statuses.append(
                        {
                            "vendor_name": company.get("company_name"),
                            "status": RequestQuote.shortlisted
                        }
                    )

            data = {
                "client_name": detailed_user.company.company_name,
                "request_custom_id": custom_id,
                "request_type": request_type,
                "asset_vin": str(vin),
                "vendor_quote_statuses": vendor_quote_statuses
            }

            payload = {"data": json.dumps(data)}

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Request/Vendor/Quote/Update/Status", payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_reject_asset_quote(asset_request_id, user):
        try:
            # Get all quotes for a request
            all_related_quotes = RequestQuoteHelper.get_asset_request_quotes_by_request_id(asset_request_id, user.db_access)
                
            # Get detailed user obj
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # Change all quotes for this request to denied
            vendor_company_info = VendorOpsHelper.get_all_vendor_companies().values(
                "company_name",
            )

            rejected_vendor_names_list = list(all_related_quotes.values_list(
                "vendor__vendor_name",
                flat=True
            ))

            if all_related_quotes:
                all_related_quotes.update(status=RequestQuote.denied)
                all_related_quotes.update(date_updated = timezone.now())

            # Add all vendors who have been denied to be updated on vendor side
            vendor_quote_statuses = []
            for company in vendor_company_info:
                if company.get("company_name") in rejected_vendor_names_list:
                    vendor_quote_statuses.append(
                        {
                            "vendor_name": company.get("company_name"),
                            "status": RequestQuote.denied
                        }
                    )
            
            request_id, custom_id, vin, request_type = RequestQuoteHelper.get_request_info_quote_obj(
                all_related_quotes[0]
            )

            data = {
                "client_name": detailed_user.company.company_name,
                "request_custom_id": custom_id,
                "request_type": request_type,
                "asset_vin": str(vin),
                "vendor_quote_statuses": vendor_quote_statuses
            }
            payload = {"data": json.dumps(data)}

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Request/Vendor/Quote/Update/Status", payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_reject_maintenance_quote(maintenance_request_id, user):
        try:
            # Get asset request
            all_related_quotes = RequestQuoteHelper.get_maintenance_quotes_by_request_id(maintenance_request_id, user.db_access)
                
            # Get detailed user obj
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # Change all other quotes for this request to denied
            vendor_company_info = VendorOpsHelper.get_all_vendor_companies().values(
                "company_name",
            )

            rejected_vendor_names_list = list(all_related_quotes.values_list(
                "vendor__vendor_name",
                flat=True
            ))

            if all_related_quotes:
                all_related_quotes.update(status=RequestQuote.denied)
                all_related_quotes.update(date_updated = timezone.now())

            # Add all vendors who have been denied to be updated on vendor side
            vendor_quote_statuses = []
            for company in vendor_company_info:
                if company.get("company_name") in rejected_vendor_names_list:
                    vendor_quote_statuses.append(
                        {
                            "vendor_name": company.get("company_name"),
                            "status": RequestQuote.denied
                        }
                    )
            
            request_id, custom_id, vin, request_type = RequestQuoteHelper.get_request_info_quote_obj(
                all_related_quotes[0]
            )

            data = {
                "client_name": detailed_user.company.company_name,
                "request_custom_id": custom_id,
                "request_type": request_type,
                "asset_vin": str(vin),
                "vendor_quote_statuses": vendor_quote_statuses
            }
            payload = {"data": json.dumps(data)}

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Request/Vendor/Quote/Update/Status", payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_reject_disposal_quote(disposal_request_id, user):
        try:
            # Get asset request
            all_related_quotes = RequestQuoteHelper.get_disposal_quotes_by_request_id(disposal_request_id, user.db_access)
                
            # Get detailed user obj
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # Change all other quotes for this request to denied
            vendor_company_info = VendorOpsHelper.get_all_vendor_companies().values(
                "company_name",
            )

            rejected_vendor_names_list = list(all_related_quotes.values_list(
                "vendor__vendor_name",
                flat=True
            ))


            if all_related_quotes:
                all_related_quotes.update(status=RequestQuote.denied)
                all_related_quotes.update(date_updated = timezone.now())

            # Add all vendors who have been denied and shortlisted to be updated on vendor side
            vendor_quote_statuses = []
            for company in vendor_company_info:
                if company.get("company_name") in rejected_vendor_names_list:
                    vendor_quote_statuses.append(
                        {
                            "vendor_name": company.get("company_name"),
                            "status": RequestQuote.denied
                        }
                    )
            
            request_id, custom_id, vin, request_type = RequestQuoteHelper.get_request_info_quote_obj(
                all_related_quotes[0]
            )

            data = {
                "client_name": detailed_user.company.company_name,
                "request_custom_id": custom_id,
                "request_type": request_type,
                "asset_vin": str(vin),
                "vendor_quote_statuses": vendor_quote_statuses
            }
            payload = {"data": json.dumps(data)}

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Request/Vendor/Quote/Update/Status", payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_reject_repair_quote(repair_request_id, user):
        try:
            # Get asset request
            all_related_quotes = RequestQuoteHelper.get_repair_quotes_by_request_id(repair_request_id, user.db_access)
                
            # Get detailed user obj
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # Change all other quotes for this request to denied
            vendor_company_info = VendorOpsHelper.get_all_vendor_companies().values(
                "company_name",
            )

            rejected_vendor_names_list = list(all_related_quotes.values_list(
                "vendor__vendor_name",
                flat=True
            ))

            if all_related_quotes:
                all_related_quotes.update(status=RequestQuote.denied)
                all_related_quotes.update(date_updated = timezone.now())

            # Add all vendors who have been denied and shortlisted to be updated on vendor side
            vendor_quote_statuses = []
            for company in vendor_company_info:
                if company.get("company_name") in rejected_vendor_names_list:
                    vendor_quote_statuses.append(
                        {
                            "vendor_name": company.get("company_name"),
                            "status": RequestQuote.denied
                        }
                    )
            
            request_id, custom_id, vin, request_type = RequestQuoteHelper.get_request_info_quote_obj(
                all_related_quotes[0]
            )

            data = {
                "client_name": detailed_user.company.company_name,
                "request_custom_id": custom_id,
                "request_type": request_type,
                "asset_vin": str(vin),
                "vendor_quote_statuses": vendor_quote_statuses
            }
            payload = {"data": json.dumps(data)}

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Request/Vendor/Quote/Update/Status", payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_reject_transfer_quote(transfer_request_id, user):
        try:
            # Get asset request
            all_related_quotes = RequestQuoteHelper.get_transfer_quotes_by_request_id(transfer_request_id, user.db_access)
                
            # Get detailed user obj
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # Change all other quotes for this request to denied
            vendor_company_info = VendorOpsHelper.get_all_vendor_companies().values(
                "company_name",
            )

            rejected_vendor_names_list = list(all_related_quotes.values_list(
                "vendor__vendor_name",
                flat=True
            ))

            if all_related_quotes:
                all_related_quotes.update(status=RequestQuote.denied)
                all_related_quotes.update(date_updated = timezone.now())

            # Add all vendors who have been denied and shortlisted to be updated on vendor side
            vendor_quote_statuses = []
            for company in vendor_company_info:
                if company.get("company_name") in rejected_vendor_names_list:
                    vendor_quote_statuses.append(
                        {
                            "vendor_name": company.get("company_name"),
                            "status": RequestQuote.denied
                        }
                    )
            
            request_id, custom_id, vin, request_type = RequestQuoteHelper.get_request_info_quote_obj(
                all_related_quotes[0]
            )

            data = {
                "client_name": detailed_user.company.company_name,
                "request_custom_id": custom_id,
                "request_type": request_type,
                "asset_vin": str(vin),
                "vendor_quote_statuses": vendor_quote_statuses
            }
            payload = {"data": json.dumps(data)}

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Request/Vendor/Quote/Update/Status", payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_reject_quotes(user, request_data):
        try:
            request_custom_id = request_data.get("request_custom_id")
            request_type  = request_data.get("request_type")
            quote_ids = request_data.get("quote_ids")

            # update statuses client side
            RequestQuoteUpdater.status_bulk_update(
                quote_ids,
                RequestQuote.denied,
                user.db_access
            )

            # update statuses vendor side
            quotes = RequestQuoteHelper.get_request_quotes_by_id_list(
                quote_ids,
                user.db_access
            ).values("id", "vendor__vendor_name")

            vendor_quote_statuses = []
            for quote in quotes:
                vendor_quote_statuses.append(
                        {
                            "vendor_name": quote.get("vendor__vendor_name"),
                            "status": RequestQuote.denied
                        }
                    )

            # Get detailed user obj
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)     

            data = {
                "client_name": detailed_user.company.company_name,
                "request_custom_id": request_custom_id,
                "request_type": request_type,
                "vendor_quote_statuses": vendor_quote_statuses
            }
            payload = {"data": json.dumps(data)}

            vendor_res = VendorOpsHelper.post_vendor_data("Client/Request/Vendor/Quote/Update/Status", payload)
            if vendor_res.status_code != status.HTTP_200_OK:
                return vendor_res

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)  