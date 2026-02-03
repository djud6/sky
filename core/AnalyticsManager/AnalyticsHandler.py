from os import stat
from django.conf import settings
from core.AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from core.RepairManager.RepairHelper import RepairHelper
from core.MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from core.MaintenanceForecastManager.MaintenanceForecastHelper import MaintenanceForecastHelper
from api.Models.Cost.license_cost import LicenseCost
from core.AnalyticsManager.AnalyticsHelper import AnalyticsHelper
from rest_framework.response import Response
from rest_framework import status
from core.FileManager.FileHelper import FileHelper
from core.AccidentManager.AccidentHelper import AccidentHelper
from core.IssueManager.IssueHelper import IssueHelper
from core.AssetManager.AssetHelper import AssetHelper
from core.DisposalManager.DisposalHelper import DisposalHelper
from core.TransferManager.TransferHelper import TransferHelper
from core.ApprovalManager.ApprovalHelper import ApprovalHelper
from core.AssetLogManager.AssetLogHelper import AssetLogHelper
from core.AssetRequestManager.AssetRequestHelper import AssetRequestHelper
from core.SnapshotManager.SnapshotHelper import SnapshotDailyCountsHelper, SnapshotDailyFleetHelper, SnapshotDailyCostHelper
from core.DailyOperationalCheckManager.DailyOperationalCheckHelper import DailyOperationalCheckHelper
from core.CostManager.CostHelper import FuelHelper, PartsHelper, LaborHelper, InsuranceHelper, RentalHelper, LicenseHelper, AcquisitionHelper, DeliveryHelper
from ..Helper import HelperMethods
from ..SnapshotManager.SnapshotHelper import SnapshotDailyCountsHelper
from GSE_Backend.errors.ErrorDictionary import CustomError

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AnalyticsHandler():

    @staticmethod
    def handle_max_users_and_assets_for_daterange(start_date, end_date, db_name):
        try:
            counts = {}
            counts_snapshots_for_month = SnapshotDailyCountsHelper.get_counts_snapshot_for_daterange(start_date, end_date, db_name)
            max_assets_for_month = counts_snapshots_for_month.order_by('-asset_count')[0].asset_count if len(counts_snapshots_for_month) > 0 else 0
            max_users_for_month = counts_snapshots_for_month.order_by('-user_count')[0].user_count if len(counts_snapshots_for_month) > 0 else 0
            counts['client'] = db_name
            counts['max_assets'] = max_assets_for_month
            counts['max_users'] = max_users_for_month
            return Response(counts, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)   

    @staticmethod
    def handle_all_max_users_and_assets_for_month():
        try:
            start_date, end_date = HelperMethods.get_datetime_range_for_this_month()
            database_names = list(settings.DATABASES.keys())
            all_companies_counts = []
            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    print("**************Processing counts for " + str(db_name) + "**************")
                    try:
                        response = AnalyticsHandler.handle_max_users_and_assets_for_daterange(start_date, end_date, db_name)
                        all_companies_counts.append(response.data)
                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))

            return FileHelper.gen_csv_response_from_list_of_dicts(all_companies_counts, 'client_asset_user_counts_' + str(start_date.strftime("%B")).lower() + '.csv')

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_data_per_asset_for_daterange(start_date, end_date, db_name):
        try:
            db_data = {}
            total_bytes = 0
            counts_snapshots_for_month = SnapshotDailyCountsHelper.get_counts_snapshot_for_daterange(start_date, end_date, db_name)
            max_assets_for_month = counts_snapshots_for_month.order_by('-asset_count')[0].asset_count

            accident_files = list(AccidentHelper.get_accident_file_entries_for_daterange(start_date, end_date, db_name).values())
            issue_files = list(IssueHelper.get_issue_file_entries_for_daterange(start_date, end_date, db_name).values())
            asset_files = list(AssetHelper.get_asset_file_entries_for_daterange(start_date, end_date, db_name).values())
            disposal_files = list(DisposalHelper.get_disposal_file_entries_for_daterange(start_date, end_date, db_name).values())
            transfer_files = list(TransferHelper.get_transfer_file_entries_for_daterange(start_date, end_date, db_name).values())
            maintenance_files = list(MaintenanceHelper.get_maintenance_file_entries_for_daterange(start_date, end_date, db_name).values())
            repair_files = list(RepairHelper.get_repair_file_entries_for_daterange(start_date, end_date, db_name).values())

            # Azure blob storage files
            total_bytes += AnalyticsHelper.sum_dict_list_value(accident_files, key="bytes")
            total_bytes += AnalyticsHelper.sum_dict_list_value(issue_files, key="bytes")
            total_bytes += AnalyticsHelper.sum_dict_list_value(asset_files, key="bytes")
            total_bytes += AnalyticsHelper.sum_dict_list_value(disposal_files, key="bytes")
            total_bytes += AnalyticsHelper.sum_dict_list_value(transfer_files, key="bytes")
            total_bytes += AnalyticsHelper.sum_dict_list_value(maintenance_files, key="bytes")
            total_bytes += AnalyticsHelper.sum_dict_list_value(repair_files, key="bytes")
            print("Blob storage")
            print(total_bytes)

            # File tables
            total_bytes += AnalyticsHelper.data_size(accident_files)
            total_bytes += AnalyticsHelper.data_size(issue_files)
            total_bytes += AnalyticsHelper.data_size(asset_files)
            total_bytes += AnalyticsHelper.data_size(disposal_files)
            total_bytes += AnalyticsHelper.data_size(transfer_files)
            total_bytes += AnalyticsHelper.data_size(maintenance_files)
            total_bytes += AnalyticsHelper.data_size(repair_files)
            print("File tables")
            print(total_bytes)

            # Accident tables
            total_bytes += AnalyticsHelper.data_size(list(AccidentHelper.get_accidents_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(AccidentHelper.get_accident_history_for_daterange(start_date, end_date, db_name).values()))
            print("Accident tables")
            print(total_bytes)

            # Approval tables
            total_bytes += AnalyticsHelper.data_size(list(ApprovalHelper.get_approval_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(ApprovalHelper.get_approval_history_for_daterange(start_date, end_date, db_name).values()))
            print("Approval tables")
            print(total_bytes)

            # Daily check tables
            total_bytes += AnalyticsHelper.data_size(list(DailyOperationalCheckHelper.get_daily_check_comments_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(DailyOperationalCheckHelper.get_daily_checks_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(DailyOperationalCheckHelper.get_daily_checks_history_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(AssetTypeChecksHelper.get_asset_type_checks_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(AssetTypeChecksHelper.get_asset_type_checks_history_for_daterange(start_date, end_date, db_name).values()))
            print("Daily check tables")
            print(total_bytes)

            # Disposal tables
            total_bytes += AnalyticsHelper.data_size(list(DisposalHelper.get_disposals_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(DisposalHelper.get_disposal_history_for_daterange(start_date, end_date, db_name).values()))
            print("Disposal tables")
            print(total_bytes)

            # Issue tables
            total_bytes += AnalyticsHelper.data_size(list(IssueHelper.get_issues_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(IssueHelper.get_issue_history_for_daterange(start_date, end_date, db_name).values()))
            print("Issue tables")
            print(total_bytes)

            # Asset log table
            total_bytes += AnalyticsHelper.data_size(list(AssetLogHelper.get_logs_for_daterange(start_date, end_date, db_name).values()))
            print("Asset log tables")
            print(total_bytes)

            # Asset tables
            total_bytes += AnalyticsHelper.data_size(list(AssetHelper.get_assets_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(AssetHelper.get_asset_history_for_daterange(start_date, end_date, db_name).values()))
            print("Asset tables")
            print(total_bytes)

            # Asset request tables
            total_bytes += AnalyticsHelper.data_size(list(AssetRequestHelper.get_asset_requests_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(AssetRequestHelper.get_asset_requests_history_for_daterange(start_date, end_date, db_name).values()))
            print("Asset request tables")
            print(total_bytes)

            # Transfer tables
            total_bytes += AnalyticsHelper.data_size(list(TransferHelper.get_transfers_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(TransferHelper.get_transfer_history_for_daterange(start_date, end_date, db_name).values()))
            print("Transfer tables")
            print(total_bytes)

            # Cost tables
            total_bytes += AnalyticsHelper.data_size(list(FuelHelper.get_fuel_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(FuelHelper.get_fuel_cost_history_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(InsuranceHelper.get_insurance_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(InsuranceHelper.get_insurance_cost_history_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(LaborHelper.get_labor_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(LaborHelper.get_labor_cost_history_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(LicenseHelper.get_license_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(LicenseHelper.get_license_cost_history_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(RentalHelper.get_rental_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(RentalHelper.get_rental_cost_history_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(PartsHelper.get_parts_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(PartsHelper.get_parts_cost_history_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(AcquisitionHelper.get_acquisition_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(AcquisitionHelper.get_acquisition_cost_history_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(DeliveryHelper.get_delivery_cost_by_date_range(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(DeliveryHelper.get_delivery_cost_history_by_date_range(start_date, end_date, db_name).values()))
            print("Cost tables")
            print(total_bytes)

            # Maintenance tables
            total_bytes += AnalyticsHelper.data_size(list(MaintenanceHelper.get_maintenance_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(MaintenanceHelper.get_maintenance_history_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(MaintenanceForecastHelper.get_maintenance_forecast_rules_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(MaintenanceForecastHelper.get_maintenance_forecast_rule_history_for_daterange(start_date, end_date, db_name).values()))
            print("Maintenance tables")
            print(total_bytes)

            # Repair tables
            total_bytes += AnalyticsHelper.data_size(list(RepairHelper.get_repairs_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(RepairHelper.get_repair_history_for_daterange(start_date, end_date, db_name).values()))
            print("Repair tables")
            print(total_bytes)

            # Snapshot tables
            total_bytes += AnalyticsHelper.data_size(list(SnapshotDailyFleetHelper.get_fleet_snapshots_in_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(SnapshotDailyCountsHelper.get_counts_snapshot_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(SnapshotDailyCountsHelper.get_location_counts_snapshot_for_daterange(start_date, end_date, db_name).values()))
            total_bytes += AnalyticsHelper.data_size(list(SnapshotDailyCostHelper.get_costs_snapshot_for_daterange(start_date, end_date, db_name).values()))
            print("Snapshot tables")
            print(total_bytes)

            bytes_per_asset = total_bytes / max_assets_for_month

            db_data['client'] = db_name
            db_data['total_bytes'] = total_bytes
            db_data['total_kilobytes'] = total_bytes/1000
            db_data['total_gigabytes'] = total_bytes/1000000000
            db_data['per_asset_bytes'] = bytes_per_asset
            db_data['per_asset_kilobytes'] = bytes_per_asset/1000
            db_data['per_asset_gigabytes'] = bytes_per_asset/1000000000

            return Response(db_data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_all_data_per_asset_for_month():
        try:
            database_names = list(settings.DATABASES.keys())
            start_date, end_date = HelperMethods.get_datetime_range_for_this_month()
            all_companies_database_data = []
            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    print("**************Processing data for " + str(db_name) + "**************")
                    try:
                        response = AnalyticsHandler.hanlde_data_per_asset_for_daterange(start_date, end_date, db_name)
                        all_companies_database_data.append(response.data)
                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))

            return FileHelper.gen_csv_response_from_list_of_dicts(all_companies_database_data, 'client_data_usage_' + str(start_date.strftime("%B")).lower() + '.csv')
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)