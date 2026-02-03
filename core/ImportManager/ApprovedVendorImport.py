from rest_framework.response import Response
from rest_framework import status
from ..ApprovedVendorsManager.ApprovedVendorsUpdater import ApprovedVendorsUpdater
from api.Models.approved_vendor_tasks import ApprovedVendorTasks
from api.Models.approved_vendor_departments import ApprovedVendorDepartments
from api.Models.approved_vendors import ApprovedVendorsModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ApprovedVendorImport():

    @staticmethod
    def import_approved_vendor_task_csv(parsed_data, db_name):
        try:
            approved_vendor_task_entries = []
            for approved_vendor_task_row in parsed_data:
                if not ApprovedVendorTasks.objects.using(db_name).filter(name=approved_vendor_task_row.get("name").strip()).exists():
                    entry = ApprovedVendorsUpdater.create_approved_vendor_task_entry(approved_vendor_task_row)
                    approved_vendor_task_entries.append(entry)
            ApprovedVendorTasks.objects.using(db_name).bulk_create(approved_vendor_task_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_12, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_12, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def import_approved_vendor_department_csv(parsed_data, db_name):
        try:
            approved_vendor_department_entries = []
            for approved_vendor_department_row in parsed_data:
                if not ApprovedVendorDepartments.objects.using(db_name).filter(name=approved_vendor_department_row.get("name").strip()).exists():
                    entry = ApprovedVendorsUpdater.create_approved_vendor_department_entry(approved_vendor_department_row)
                    approved_vendor_department_entries.append(entry)
            ApprovedVendorDepartments.objects.using(db_name).bulk_create(approved_vendor_department_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_12, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_12, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def import_approved_vendor_csv(parsed_data, db_name):
        try:
            approved_vendor_entries = []
            for approved_vendor_row in parsed_data:
                if not ApprovedVendorsModel.objects.using(db_name).filter(vendor_name=approved_vendor_row.get("vendor_name").strip()).exists():
                    entry = ApprovedVendorsUpdater.create_approved_vendor_entry(approved_vendor_row, db_name)
                    approved_vendor_entries.append(entry)
            ApprovedVendorsModel.objects.using(db_name).bulk_create(approved_vendor_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_12, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_12, e), status=status.HTTP_400_BAD_REQUEST)
