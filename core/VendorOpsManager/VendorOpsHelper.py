from email import header
from os import stat
import statistics
from rest_framework.response import Response
from rest_framework import status
from api_auth.Auth_User.Company import Company
import api.Serializers.serializers as sers
import requests
import json
from django.conf import settings
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class VendorOpsHelper:

    # Authentication Helper Methods
    # ------------------------------------------------------------------------------------------

    @staticmethod
    def auth_and_send_request(url, action="get", payload={}, files=[]):
        try:
            headers = json.loads(settings.INTERNAL_INTEGRATION_SYSTEM_HEADERS)
            if action == "get":
                res = requests.get(url, headers=headers, data=payload)
            elif action == "post":
                res = requests.post(url, headers=headers, data=payload, files=files)
            elif action == "delete":
                res = requests.delete(url, headers=headers)
            elif action == "patch":
                res = requests.patch(url, headers=headers, data=payload, files=files)
            return res

        except requests.exceptions.ConnectionError:
            print("CONNECTION REFUSED")
            Logger.getLogger().error("CONNECTION REFUSED")

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return CustomError.get_full_error_json(CustomError.G_0, e)

    # Vendor Data Methods
    # ------------------------------------------------------------------------------------------

    @staticmethod
    def process_response(response):
        try:
            try:
                response_body = response.json()
            except Exception:
                response_body = {}
            if int(response.status_code) >= 400:
                return Response(response_body, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(response_body, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def get_vendor_data(endpoint, payload):
        base_url = settings.VENDOR_SYSTEM_BASE_URL
        URL = base_url + endpoint
        body = payload
        try:
            res = VendorOpsHelper.auth_and_send_request(URL, "get", body)
            return VendorOpsHelper.process_response(res)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def patch_vendor_data(endpoint, payload, files=[]):
        base_url = settings.VENDOR_SYSTEM_BASE_URL
        URL = base_url + endpoint
        body = payload
        try:
            res = VendorOpsHelper.auth_and_send_request(URL, "patch", body, files)
            return VendorOpsHelper.process_response(res)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post_vendor_data(endpoint, payload, files=[]):
        base_url = settings.VENDOR_SYSTEM_BASE_URL
        URL = base_url + endpoint
        body = payload
        try:
            res = VendorOpsHelper.auth_and_send_request(URL, "post", body, files)
            return VendorOpsHelper.process_response(res)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------

    @staticmethod
    def get_auth_db_company_by_name(company_name):
        try:
            return Company.objects.using("auth_db").get(company_name=company_name), Response(
                status=status.HTTP_302_FOUND
            )
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.VIDDNE_1, e))
            return None, Response(
                CustomError.get_full_error_json(CustomError.VIDDNE_1, e), status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_all_vendor_companies():
        return Company.objects.using("auth_db").filter(company_type="vendor")

    @staticmethod
    def get_vendor_companies_by_names(vendor_names):
        return Company.objects.using("auth_db").filter(company_name__in=vendor_names)

    @staticmethod
    def get_all_auth_db_companies():
        return Company.objects.using("auth_db").all()

    @staticmethod
    def get_client_db_access_dict():
        auth_companies = VendorOpsHelper.get_all_auth_db_companies().values()
        company_db_access = {}
        for company in auth_companies:
            company_db_access[company.get("company_name")] = company.get("company_db_access")
        return company_db_access

    @staticmethod
    def get_client_db_access_by_company_name(company_name):
        try:
            return Company.objects.using("auth_db").get(
                company_name=company_name
                ).company_db_access
        except Exception as e:
            return "default"