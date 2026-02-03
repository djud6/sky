from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from multiprocessing.pool import ThreadPool

from api.Models.approved_vendor_departments import ApprovedVendorDepartments
from api.Models.approved_vendor_tasks import ApprovedVendorTasks
from api.Models.asset_model import AssetModel
from api.Models.approved_vendors import ApprovedVendorsModel
from core.Helper import HelperMethods
from core.VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from .ApprovedVendorsHelper import ApprovedVendorsHelper
from .ApprovedVendorsUpdater import ApprovedVendorsUpdater
from api.Serializers.serializers import (
    ApprovedVendorSerializer,
    LightApprovedVendorSerializer,
    ApprovedVendorDepartmentsSerializer, ApprovedVendorTasksSerializer,
)
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class ApprovedVendorsHandler():

    @staticmethod
    def handle_get_approved_vendors_by_task_and_department(dep_id, task_id, user):
        try:
            approved_vendors = ApprovedVendorsHelper.select_related_to_approved_vendor(ApprovedVendorsHelper.get_vendors_by_dept_and_task(dep_id, task_id, user.db_access))
            serializer = ApprovedVendorSerializer(approved_vendors, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_departments(user):
        try:
            approved_vendor_departments = ApprovedVendorDepartments.objects.using(user.db_access).all()
            serializer = ApprovedVendorDepartmentsSerializer(approved_vendor_departments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_add_approved_vendor(request_data):
        try:
            client_name = request_data.get("client_name")
            auth_company, resp = VendorOpsHelper.get_auth_db_company_by_name(client_name)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp

            db_name = auth_company.company_db_access

            # Check if vendor already added
            if ApprovedVendorsHelper.vendor_exists_by_name(request_data.get("vendor_name"), db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VAE_0))
                return Response(
                    CustomError.get_full_error_json(CustomError.VAE_0),
                    status=status.HTTP_400_BAD_REQUEST
                )

            approved_vendor_entry = ApprovedVendorsUpdater.create_approved_vendor_entry(
                request_data,
                db_name
            )

            vendor = approved_vendor_entry.save(using=db_name)

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST
            )

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_tasks(user):
        try:
            approved_vendor_tasks = ApprovedVendorTasks.objects.using(user.db_access).all()
            serializer = ApprovedVendorTasksSerializer(approved_vendor_tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_vendors_by_department(_dep_id, user):
        try:
            vendors = ApprovedVendorsHelper.select_related_to_approved_vendor(
                ApprovedVendorsModel.objects.using(user.db_access).filter(vendor_department__id=_dep_id))
            ser = ApprovedVendorSerializer(vendors, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_vendors_by_task(_task_id, user):
        try:
            vendors = ApprovedVendorsHelper.select_related_to_approved_vendor(
                ApprovedVendorsModel.objects.using(user.db_access).filter(vendor_task__id=_task_id))
            ser = ApprovedVendorSerializer(vendors, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_vendors(user):
        try:
            vendors = ApprovedVendorsHelper.select_related_to_approved_vendor(ApprovedVendorsHelper.get_all_vendors(user.db_access))
            ser = LightApprovedVendorSerializer(vendors, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_vendor_services(payload):
        try:
            client_db_access_dict = VendorOpsHelper.get_client_db_access_dict()
            vendor_name = payload.get("vendor_name")
            client_names = payload.get("client_names")
            # parse service config
            service_config_pre_parse = payload.get("service_config")
            service_config = {}
            for service in service_config_pre_parse:
                service_config[service.get("service_type")] = service.get("provided_by_vendor")

            def update_vendor_services(client_info):
                try:
                    client_db_access = client_db_access_dict.get(client_info.get("client_name"))
                    # expecting task_config to be a dict with every task as key and a bool value
                    ApprovedVendorsUpdater.update_vendor_services(
                        vendor_name,
                        service_config,
                        client_db_access
                    )

                except Exception as e:
                    Logger.getLogger().error(CustomError.get_error_dev(e))

            database_names = list(settings.DATABASES.keys())

            with ThreadPool(processes=int(10 if len(database_names) > 10 else len(database_names))) as pool:
                pool.map(update_vendor_services, client_names)

            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST
            )

    # ---------------------------------------------------------------------------------------------------------------------          
    
    @staticmethod
    def handle_get_all_available_vendors():
        endpoint = 'Client/Vendor/Get/List'

        try:
            res = VendorOpsHelper.get_vendor_data(endpoint, {})
            return res.data
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
