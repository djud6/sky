from rest_framework.response import Response
from rest_framework import status
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.maintenance_request_history import MaintenanceRequestModelHistory
from api.Models.maintenance_forecast_history import MaintenanceForecastRulesHistory
from api.Models.asset_log import AssetLog
from .AssetHistory import AssetHistory
from ..AssetManager.AssetHelper import AssetHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class MaintenanceHistory():

    @staticmethod
    def create_maintenance_records(maintenance_obj_list):
        for maintenance_obj in maintenance_obj_list:
            if(not MaintenanceHistory.create_maintenance_record_by_obj(maintenance_obj)):
                return False
        return True
            
    @staticmethod
    def create_maintenance_record(maintenance_id, db_name):
        try:
            maintenance_request = MaintenanceRequestModel.objects.using(db_name).get(maintenance_id=maintenance_id)
            maintenance_request_history_entry = MaintenanceHistory.generate_maintenance_request_history_entry(maintenance_request)
            maintenance_request_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_maintenance_record_by_obj(maintenance_request):
        try:
            maintenance_request_history_entry = MaintenanceHistory.generate_maintenance_request_history_entry(maintenance_request)
            maintenance_request_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_maintenance_request_history_entry(maintenance_request):
        return MaintenanceRequestModelHistory(
            maintenance=maintenance_request,
            work_order=maintenance_request.work_order,
            inspection_type=maintenance_request.inspection_type,
            assigned_vendor=maintenance_request.assigned_vendor,
            location=maintenance_request.location,
            date_completed=maintenance_request.date_completed,
            estimated_delivery_date=maintenance_request.estimated_delivery_date,
            requested_delivery_date=maintenance_request.requested_delivery_date,
            vendor_contacted_date=maintenance_request.vendor_contacted_date,
            available_pickup_date=maintenance_request.available_pickup_date,
            vendor_email=maintenance_request.vendor_email,
            mileage=maintenance_request.mileage,
            hours=maintenance_request.hours,
            modified_by=maintenance_request.modified_by,
            status= maintenance_request.status
        )

    @staticmethod
    def create_maintenance_event_log(maintenance_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(maintenance_obj.VIN, AssetLog.maintenance, maintenance_obj.work_order, maintenance_obj.modified_by, description, maintenance_obj.location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_2, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_2, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_added_maintenance_event_logs(maintenance_obj_list):
        for maintenance_obj in maintenance_obj_list:
            description = "Maintenance request " + str(maintenance_obj.work_order) + " was created."
            event_log_response = MaintenanceHistory.create_maintenance_event_log(maintenance_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response
        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def batch_history_and_logs_for_asset_status_change_by_maintenance(maintenance_qs, status_update, db_name):
        # The `iterator()` method ensures only a few rows are fetched from
        # the database at a time, saving memory.
        for maintenance in maintenance_qs.iterator():
            # create asset history record
            asset_obj = AssetHelper.get_asset_by_VIN(maintenance.VIN, db_name)
            if(not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Asset was set to " + str(status_update) + " due to maintenance " + str(maintenance.work_order)
            event_log_response = MaintenanceHistory.create_maintenance_event_log(maintenance, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

        return Response(status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------------------------------------------    

    @staticmethod
    def create_maintenance_forecast_record(maintenance_rule_obj):
        try:
            maintenance_forecast_history_entry = MaintenanceHistory.generate_maintenance_forecast_history_entry(maintenance_rule_obj)
            maintenance_forecast_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_maintenance_forecast_history_entry(maintenance_rule_obj):
        return MaintenanceForecastRulesHistory(
            maintenance_forecast = maintenance_rule_obj,
            custom_id = maintenance_rule_obj.custom_id,
            modified_by=maintenance_rule_obj.modified_by,
            hour_cycle=maintenance_rule_obj.hour_cycle,
            mileage_cycle=maintenance_rule_obj.mileage_cycle,
            time_cycle=maintenance_rule_obj.time_cycle,
            linked_engine=maintenance_rule_obj.linked_engine
        )

    @staticmethod
    def create_maintenance_rule_event_log(maintenance_rule_obj, description):
        try:
            event_log_entry = AssetHistory.generate_asset_log_event_entry(maintenance_rule_obj.VIN, AssetLog.maintenance_rule, maintenance_rule_obj.custom_id, maintenance_rule_obj.modified_by, description, maintenance_rule_obj.VIN.current_location)
            event_log_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ALF_2, e))
            return Response(CustomError.get_full_error_json(CustomError.ALF_2, e), status=status.HTTP_400_BAD_REQUEST)