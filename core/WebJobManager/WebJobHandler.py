from api.Models.Snapshot.snapshot_daily_location_counts import SnapshotDailyLocationCounts
from core.FileManager.PdfManager import PdfManager
from api.Models.DetailedUser import DetailedUser
from api.Models.Snapshot.snapshot_daily_counts import SnapshotDailyCounts
from core.UserManager.UserHelper import UserHelper
from api.Models.Cost.fuel_cost import FuelCost
from api.Models.Snapshot.snapshot_daily_currency import SnapshotDailyCurrency
from api.Models.Snapshot.snapshot_daily_location_cost import SnapshotDailyLocationCost
from rest_framework.response import Response
from rest_framework import status
from django import db
from django.conf import settings
from datetime import date
from datetime import datetime
import requests
from django.utils import timezone
import itertools
from core.Helper import HelperMethods
from core.AccidentManager.AccidentHelper import AccidentHelper
from core.IssueManager.IssueHelper import IssueHelper
from core.AssetManager.AssetHelper import AssetHelper
from core.SnapshotManager.SnapshotUpdater import SnapshotDailyCountsUpdater, SnapshotDailyFleetUpdater, SnapshotDailyCostUpdater, SnapshotDailyCurrencyUpdater
from core.SnapshotManager.SnapshotHelper import SnapshotDailyFleetHelper, SnapshotDailyCostHelper, SnapshotDailyCountsHelper, SnapshotDailyCurrencyHelper
from ..MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from ..MaintenanceForecastManager.MaintenanceForecastHelper import MaintenanceForecastHelper
from ..InspectionTypeManager.InspectionTypeHelper import InspectionTypeHelper
from ..RepairManager.RepairHelper import RepairHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..LocationManager.LocationHelper import LocationHelper
from ..ChartCalculations.ChartCalculationsHelper import ChartCalculationsHelper
from ..AssetManager.AssetUpdater import AssetUpdater
from ..CostManager.CostHelper import FuelHelper, LicenseHelper, RentalHelper, LaborHelper, PartsHelper, InsuranceHelper, AcquisitionHelper, DeliveryHelper
from ..CompanyManager.CompanyHelper import CompanyHelper
from ..CurrencyManager.CurrencyHelper import CurrencyHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from .WebJobHelper import WebJobHelper
from ..HistoryManager.MaintenanceHistory import MaintenanceHistory
from ..HistoryManager.RepairHistory import RepairHistory
from api.Models.asset_model import AssetModel
from api.Models.Snapshot.snapshot_daily_asset import SnapshotDailyAsset
from communication.EmailService.EmailService import Email
from api.Serializers.serializers import AssetModelSerializer, DeliveryCostSerializer, LicenseCostSerializer
from api.Serializers.serializers import FuelCostSerializer, PartCostSerializer, RentalCostSerializer, LaborCostSerializer, InsuranceCostSerializer, AcquisitionCostSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
from core.PusherManager.PusherHelper import PusherHelper
from azure.servicebus import ServiceBusClient


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class WebJobHandler():

    # -----------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_maintenance_and_repair_set_asset_inop():
        try:
            database_names = list(settings.DATABASES.keys())
            current_datetime = timezone.now()
            day_start_datetime = current_datetime.replace(hour=00, minute=00, second=00, microsecond=000000)
            day_end_datetime = current_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            print("Date range start: " + str(day_start_datetime))
            print("Date range end: " + str(day_end_datetime))
            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default', 'axys', 'demo_1', 'demo_2', 'demo_4', 'demo_5',
                               'demo_aukai', 'demo_generic', 'demo_lokomotive', 'demo_orion', 'dev_demo',
                               'dev_demo_aukai', 'dev_staging', 'fmt', 'gbcs', 'lloydminster', 'mobile_app',
                               'schlumberger', 'westjet']
                if db_name not in dbs_to_skip:
                    print("--------------------")
                    print(db_name)
                    print("--------------------")
                    maintenance_response = WebJobHandler.maintenance_set_asset_inop(day_start_datetime, day_end_datetime, db_name)
                    if maintenance_response.status_code != status.HTTP_200_OK:
                        return maintenance_response
                    repair_response = WebJobHandler.repair_set_asset_inop(day_start_datetime, day_end_datetime, db_name)
                    if repair_response.status_code != status.HTTP_200_OK:
                        return repair_response
                else:
                    print("Skipping " + db_name + "...")
            
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def maintenance_set_asset_inop(day_start_datetime, day_end_datetime, db_name):

        print("MAINTENANCE")
        maintenance_qs = MaintenanceHelper.get_maintenance_for_inop_in_daterange(day_start_datetime, day_end_datetime, db_name)
        maintenance_vins = list(maintenance_qs.values_list('VIN', flat=True))
        print(maintenance_vins)

        print("Updating assets...")
        update_response = AssetUpdater.update_status_for_assets_in_list(maintenance_vins, AssetModel.Inop, db_name)
        if update_response.status_code != status.HTTP_202_ACCEPTED:
            return update_response
        
        print("Generating history and logs...")
        maintenance_qs = MaintenanceHelper.get_maintenance_in_vinlist_and_daterange(day_start_datetime, day_end_datetime, maintenance_vins, db_name)
        history_and_log_response = MaintenanceHistory.batch_history_and_logs_for_asset_status_change_by_maintenance(maintenance_qs, AssetModel.Inop, db_name)
        if history_and_log_response.status_code != status.HTTP_201_CREATED:
            return history_and_log_response

        return Response(status=status.HTTP_200_OK)


    @staticmethod
    def repair_set_asset_inop(day_start_datetime, day_end_datetime, db_name):

        print("REPAIRS")
        repair_qs = RepairHelper.get_repairs_for_inop_in_daterange(day_start_datetime, day_end_datetime, db_name)
        repair_vins = list(repair_qs.values_list('VIN', flat=True))
        print(repair_vins)
        
        print("Updating assets...")
        update_response = AssetUpdater.update_status_for_assets_in_list(repair_vins, AssetModel.Inop, db_name)
        if update_response.status_code != status.HTTP_202_ACCEPTED:
            return update_response
        
        print("Generating history and logs...")
        repair_qs = RepairHelper.get_repairs_in_vinlist_and_daterange(day_start_datetime, day_end_datetime, repair_vins, db_name)
        history_and_log_response = RepairHistory.batch_history_and_logs_for_asset_status_change_by_repair(repair_qs, AssetModel.Inop, db_name)
        if history_and_log_response.status_code != status.HTTP_201_CREATED:
            return history_and_log_response

        return Response(status=status.HTTP_200_OK)

    
    # -----------------------------------------------------------------------------------------------------------


    @staticmethod
    def handle_create_fleet_daily_snapshot():
        try:
            database_names = list(settings.DATABASES.keys())
            day_start, day_end = HelperMethods.get_datetime_range_for_today()

            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    try:
                        print("Attempting snapshot for db: " + str(db_name))
                        all_assets = AssetHelper.select_related_to_asset(AssetHelper.get_all_assets(db_name))
                        all_assets_serialiazed = AssetModelSerializer(all_assets, many=True)
                        all_assets_serialiazed_data = all_assets_serialiazed.data
                        snapshot_entries = []
                        for asset in all_assets_serialiazed_data:
                            entry = SnapshotDailyFleetUpdater.create_snapshot_daily_asset_entry(asset)
                            snapshot_entries.append(entry)

                        # (Placed check here and not in beginning to allow for easier debugging)
                        if not SnapshotDailyFleetHelper.fleet_snapshot_exists_for_daterange(day_start, day_end, db_name):
                            SnapshotDailyAsset.objects.using(db_name).bulk_create(snapshot_entries)
                            print("Snapshot has been created.")
                        else:
                            print("Fleet snapshot already exists for today.")

                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.SSF_0, e))
                        print(CustomError.get_error_dev(CustomError.SSF_0, e))

                else:
                    print("Skipping " + db_name + "...")

            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    # -----------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_create_cost_daily_snapshot():
        try:
            database_names = list(settings.DATABASES.keys())
            day_start, day_end = HelperMethods.get_datetime_range_for_today()
            print("Today daterange (UTC): " + str(day_start) + " - " + str(day_end))
            
            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    try:
                        print("*******************************************************************************")
                        print("Starting snapshot for: " + str(db_name))

                        company = CompanyHelper.get_list_companies(db_name)[0]
                        standardized_currency = CompanyHelper.get_standard_currency_by_company_obj(company, db_name)
                        all_locations = LocationHelper.get_all_locations(db_name).values_list('location_id', flat=True)
                        all_assets = AssetHelper.get_all_assets(db_name).exclude(current_location=None).values_list('current_location', 'VIN')
                        all_accidents = AccidentHelper.get_all_accidents(db_name).exclude(location=None).values_list('location', 'accident_id')
                        all_maintenance = MaintenanceHelper.get_all_maintenance(db_name).exclude(location=None).values_list('location', 'maintenance_id')
                        all_issues = IssueHelper.get_all_issues(db_name).exclude(location=None).values_list('location', 'issue_id')
                        all_disposals = DisposalHelper.get_asset_disposals(db_name).exclude(location=None).values_list('location', 'id')

                        all_fuel_costs = FuelCostSerializer(FuelHelper.get_fuel_cost_by_date_range(day_start, day_end, db_name), many=True).data
                        all_parts_costs = PartCostSerializer(PartsHelper.get_parts_cost_by_date_range(day_start, day_end, db_name), many=True).data
                        all_labor_costs = LaborCostSerializer(LaborHelper.get_labor_cost_by_date_range(day_start, day_end, db_name), many=True).data
                        all_insurance_costs = InsuranceCostSerializer(InsuranceHelper.get_insurance_cost_by_date_range(day_start, day_end, db_name), many=True).data
                        all_license_costs = LicenseCostSerializer(LicenseHelper.get_license_cost_by_date_range(day_start, day_end, db_name), many=True).data
                        all_acquisition_costs = AcquisitionCostSerializer(AcquisitionHelper.get_acquisition_cost_by_date_range(day_start, day_end, db_name), many=True).data
                        all_rental_costs = RentalCostSerializer(RentalHelper.get_rental_cost_by_date_range(day_start, day_end, db_name), many=True).data
                        all_delivery_costs = DeliveryCostSerializer(DeliveryHelper.get_delivery_cost_by_date_range(day_start, day_end, db_name), many=True).data

                        daily_location_cost_entries = []

                        for location_id in all_locations:
                            
                            # Get all assets in current location
                            assets_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_assets)
                            # Get all accidents for current location
                            accident_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_accidents)
                            # Get all maintenance for current location
                            maintenance_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_maintenance)
                            # Get all issues for current location
                            issues_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_issues)
                            # Get all maintenance for current location
                            disposal_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_disposals)

                            # These lists will hold the vins and ids that are relevant to this location
                            asset_vins = []
                            accidents_ids = []
                            maintenance_ids = []
                            issue_ids = []
                            disposal_ids = []
                            if len(assets_subset) > 0:
                                asset_locations, asset_vins = zip(*assets_subset)
                            if len(accident_subset) > 0:
                                accident_locations, accidents_ids = zip(*accident_subset)
                            if len(maintenance_subset) > 0:
                                maintenance_locations, maintenance_ids = zip(*maintenance_subset)
                            if len(issues_subset) > 0:
                                issue_locations, issue_ids = zip(*issues_subset)
                            if len(disposal_subset) > 0:
                                disposal_locations, disposal_ids = zip(*disposal_subset)

                            # Will hold cumilitive cost values for this location
                            daily_cost_dict = {
                                "currency": standardized_currency,
                                "volume_unit": 'NA',
                                "location": location_id,
                                "volume_fuel": 0,
                                "total_cost_fuel": 0,
                                "taxes_fuel": 0,
                                "deductible": 0,
                                "total_cost_insurance": 0,
                                "total_base_hours": 0,
                                "total_overtime_hours": 0,
                                "total_cost_labor": 0,
                                "taxes_labor": 0,
                                "license_registration_cost": 0,
                                "license_plate_renewal_cost": 0,
                                "total_cost_license": 0,
                                "taxes_license": 0,
                                "total_cost_acquisition": 0,
                                "taxes_acquisition": 0,
                                "total_cost_parts": 0,
                                "taxes_parts": 0,
                                "total_cost_rental": 0,
                                "total_cost_delivery": 0,
                                "taxes_delivery": 0
                            }
                            
                            print("------------ LOCATION: " + str(location_id) + " ------------")
                            
                            # Today's fuel costs for this location -----------------------------------------------------------------------------
                            fuel_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('location', [location_id], all_fuel_costs)
                            for fuel_cost_entry in fuel_costs_for_location:
                                daily_cost_dict['volume_fuel'] += FuelHelper.get_fuel_volume_in_liters(fuel_cost_entry.get('volume'), fuel_cost_entry.get('volume_unit'))
                                daily_cost_dict['total_cost_fuel'] += fuel_cost_entry.get('total_cost')
                                daily_cost_dict['taxes_fuel'] += fuel_cost_entry.get('taxes')

                            print("volume_fuel: " + str(daily_cost_dict.get('volume_fuel')))
                            print("total_cost_fuel: " + str(daily_cost_dict.get('total_cost_fuel')))
                            print("taxes_fuel: " + str(daily_cost_dict.get('taxes_fuel')))

                            # Today's insurance costs for this location ------------------------------------------------------------------------
                            insurance_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('location', [location_id], all_insurance_costs)
                            for insurance_entry in insurance_costs_for_location:
                                daily_cost_dict['deductible'] += insurance_entry.get("deductible")
                                daily_cost_dict['total_cost_insurance'] += insurance_entry.get("total_cost")

                            print("deductible: " + str(daily_cost_dict.get('deductible')))
                            print("total_cost_insurance: " + str(daily_cost_dict.get('total_cost_insurance')))

                            # Today's labor costs for this location ----------------------------------------------------------------------------
                            labor_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('location', [location_id], all_labor_costs)
                            for labor_cost_entry in labor_costs_for_location:
                                daily_cost_dict['total_base_hours'] += labor_cost_entry.get("total_base_hours")
                                daily_cost_dict['total_overtime_hours'] += labor_cost_entry.get("total_overtime_hours")
                                daily_cost_dict['total_cost_labor'] += labor_cost_entry.get("total_cost")
                                daily_cost_dict['taxes_labor'] += labor_cost_entry.get("taxes")

                            print("total_base_hours: " + str(daily_cost_dict.get('total_base_hours')))
                            print("total_overtime_hours: " + str(daily_cost_dict.get('total_overtime_hours')))
                            print("total_cost_labor: " + str(daily_cost_dict.get('total_cost_labor')))
                            print("taxes_labor: " + str(daily_cost_dict.get('taxes_labor')))

                            # Today's license costs for this location -------------------------------------------------------------------------
                            license_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('location', [location_id], all_license_costs)
                            for license_entry in license_costs_for_location:
                                daily_cost_dict['license_registration_cost'] += license_entry.get("license_registration")
                                daily_cost_dict['license_plate_renewal_cost'] += license_entry.get("license_plate_renewal")
                                daily_cost_dict['total_cost_license'] += license_entry.get("total_cost")
                                daily_cost_dict['taxes_license'] += license_entry.get("taxes")

                            print("license_registration_cost: " + str(daily_cost_dict.get('license_registration_cost')))
                            print("license_plate_renewal_cost: " + str(daily_cost_dict.get('license_plate_renewal_cost')))
                            print("total_cost_license: " + str(daily_cost_dict.get('total_cost_license')))
                            print("taxes_license: " + str(daily_cost_dict.get('taxes_license')))

                            # Today's acquisition costs for this location -------------------------------------------------------------------------
                            acquisition_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('VIN', asset_vins, all_acquisition_costs)
                            for acquisition_entry in acquisition_costs_for_location:
                                daily_cost_dict['total_cost_acquisition'] += acquisition_entry.get("total_cost")
                                daily_cost_dict['taxes_acquisition'] += acquisition_entry.get("taxes")

                            print("acquisition_cost: " + str(daily_cost_dict.get('total_cost_acquisition')))

                            # Today's parts costs for this location --------------------------------------------------------------------------
                            parts_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('location', [location_id], all_parts_costs)
                            for parts_cost_entry in parts_costs_for_location:
                                daily_cost_dict['total_cost_parts'] += parts_cost_entry.get("total_cost")
                                daily_cost_dict['taxes_parts'] += parts_cost_entry.get("taxes")

                            print("total_cost_parts: " + str(daily_cost_dict.get('total_cost_parts')))
                            print("taxes_parts: " + str(daily_cost_dict.get('taxes_parts')))

                            # Today's rental costs for this location --------------------------------------------------------------------------
                            rental_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('location', [location_id], all_rental_costs)
                            for rental_entry in rental_costs_for_location:
                                daily_cost_dict['total_cost_rental'] += rental_entry.get("total_cost")

                            # Today's delivery costs for this location --------------------------------------------------------------------------
                            delivery_costs_for_location = ChartCalculationsHelper.get_dict_subset_in_field_list('location', [location_id], all_delivery_costs)
                            for delivery_entry in delivery_costs_for_location:
                                daily_cost_dict['total_cost_delivery'] += delivery_entry.get("total_cost")
                                daily_cost_dict['taxes_delivery'] += delivery_entry.get("taxes")

                            print("total_cost_rental: " + str(daily_cost_dict.get('total_cost_rental')))

                            # Create cost entry for today for this location and append to list
                            daily_location_cost_entries.append(SnapshotDailyCostUpdater.create_snapshot_cost_daily_entry(daily_cost_dict))

                        print("---------------------------------------")
                        # if snapshot for today doesn't exist... (Placed check here and not in beginning to allow for easier debugging)
                        if not SnapshotDailyCostHelper.cost_snapshot_exists_for_daterange(day_start, day_end, db_name):
                            # Create all the entries in the database
                            SnapshotDailyLocationCost.objects.using(db_name).bulk_create(daily_location_cost_entries)
                            print("Snapshot has been created.")
                        else:
                            print("Cost snapshot already exists for today.")
                        print("---------------------------------------")

                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.SSF_1, e))
                        print("SSF-1: Daily Cost Snapshot has failed for db " + str(db_name))

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    
    # -----------------------------------------------------------------------------------------------------------


    @staticmethod
    def handle_create_daily_counts_snapshot():
        try:
            database_names = list(settings.DATABASES.keys())
            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    try:
                        print("**********************************************************************************")
                        print("Adding counts for database " + str(db_name) + ":")

                        day_start, day_end = HelperMethods.get_datetime_range_for_today()

                        if not SnapshotDailyCountsHelper.counts_snapshot_exists_for_daterange(day_start, day_end, db_name):
                            daily_counts_dict = {
                                "asset_count": AssetHelper.get_all_assets_at_company(db_name).count(),
                                "user_count": UserHelper.get_all_active_users_for_company(db_name).count()
                            }

                            daily_counts_obj = SnapshotDailyCountsUpdater.create_snapshot_daily_counts(daily_counts_dict, db_name)
                            
                            print("asset_count: " + str(daily_counts_obj.asset_count))
                            print("user_count: " + str(daily_counts_obj.user_count))
                        else:
                            print("Entry for asset_count and user count today already exists.")

                        day_start, day_end = HelperMethods.get_datetime_range_for_yesterday()
                        if not SnapshotDailyCountsHelper.location_counts_snapshot_exists_for_daterange(day_start, day_end, db_name):
                            snapshot_count_entries = []
                            daily_location_counts = ChartCalculationsHelper.get_daily_checks_and_assets(db_name)
                            for daily_location_count in daily_location_counts:
                                entry = SnapshotDailyCountsUpdater.create_snapshot_daily_location_counts(daily_location_count, db_name)
                                snapshot_count_entries.append(entry)
                            SnapshotDailyLocationCounts.objects.using(db_name).bulk_create(snapshot_count_entries)
                            print("Created entries for daily location counts.")
                        else:
                            print("Entry for asset_counts and daily checks per location already exists.")

                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                        print(CustomError.get_error_dev(CustomError.G_0, e))

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    # -----------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_create_daily_currency_snapshot():
        try:
            database_names = list(settings.DATABASES.keys())

            # get the response from the currency conversion api
            currency_response = WebJobHelper.get_currency_exchange_response()
            
            # make sure the currency conversion api call works - otherwise return an error
            if currency_response.status_code != status.HTTP_200_OK:
                return Response(CustomError.get_full_error_json(CustomError.CEE_0), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            day_start, day_end = HelperMethods.get_datetime_range_for_today()

            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    try:
                        print("**********************************************************************************")
                        print("Adding currency snapshots for database " + str(db_name) + ":")
                        if not SnapshotDailyCurrencyHelper.currency_snapshot_exists_for_daterange(day_start, day_end, db_name):
                            standard_currency = CompanyHelper.get_standard_currency_code_by_company_obj(CompanyHelper.get_list_companies(db_name)[0], db_name)
                            SnapshotDailyCurrencyUpdater.update_snapshot_currencies(currency_response.json()['rates'], standard_currency, db_name)
                        else:
                            print("Entry for currency values already exist.")

                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.SSF_3, e))
                        print(CustomError.get_error_dev(CustomError.SSF_3, e))

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_notify_maintenance():
        try:
            database_names = list(settings.DATABASES.keys())
            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    try:
                        print("**********************************************************************************")
                        print("Processing maintenance notifications for database " + str(db_name) + ":")
                        day_start, day_end = HelperMethods.get_datetime_range_for_today()

                        # NOTE: Uncomment two lines below to test
                        day_start = HelperMethods.datetime_string_to_datetime("2000-02-02 00:00:00.000000")
                        day_end = HelperMethods.datetime_string_to_datetime("2028-02-02 00:00:00.000000")

                        all_inspection_names = InspectionTypeHelper.get_all_inspection_types(db_name).values_list('inspection_name', flat=True)

                        inrange_rule_list, potential_rule_list, forecast_response = MaintenanceForecastHelper.forecast_maintenance(db_name, all_inspection_names, day_start, day_end)
                        # Determine the difference between overdue assets vs due soon assets
                        #check for the notifications of each against its database

                        #OVER DUE SHITED NOTIFICATION LOGIC
                        #remove items from the list that have their shifted notification time in the future
                        
                        shifted_overdue_list = list()
                        shifted_due_soon_list = list()
                        for asset in inrange_rule_list:
                            #Check to see if asset overdue is not null
                            print("Origional Maintenance Date: "+str(asset[4]))
                            if(asset[5]['asset_overdue_date_variance'] is not None): #check asset
                                shifted_maintenance_date = HelperMethods.shift_overdue_date(asset[4], asset[5]['asset_overdue_date_variance'])
                                #check to see if the shifted overdue date is past:
                                if(shifted_maintenance_date <= datetime.utcnow()):
                                    print("*** ADDING ASSET TO SHIFTED OVERDUE LIST "+asset[0])
                                    shifted_overdue_list.append(asset)
                                else: #check for due soon status
                                    if(asset[5]['asset_due_soon_date_variance'] is not None):
                                        shifted_maintenance_date = HelperMethods.shift_overdue_date(asset[4], asset[5]['asset_due_soon_date_variance'])
                                        if(shifted_maintenance_date <= datetime.utcnow() and datetime.utcnow() <= asset[4]):
                                            print("*** ADDING ASSET TO SHIFTED DUE SOON LIST "+asset[0])
                                            shifted_due_soon_list.append(asset)
                            elif(asset[5]['asset_type_overdue_date_variance'] is not None): #check assettype
                                shifted_maintenance_date = HelperMethods.shift_overdue_date(asset[4], asset[5]['asset_type_overdue_date_variance'])
                                if(shifted_maintenance_date <= datetime.utcnow()):
                                    print("*** ADDING ASSET TO SHIFTED OVERDUE LIST "+asset[0])
                                    shifted_overdue_list.append(asset)
                                else:
                                    if(asset[5]['asset_type_due_soon_date_variance'] is not None):
                                        shifted_maintenance_date = HelperMethods.shift_overdue_date(asset[4], asset[5]['asset_type_due_soon_date_variance'])
                                        if(shifted_maintenance_date <= datetime.utcnow() and datetime.utcnow() <= asset[4]):
                                            print("*** ADDING ASSET TO SHIFTED DUE SOON LIST "+asset[0])
                                            shifted_due_soon_list.append(asset)
                            else:
                                shifted_maintenance_date = asset[4]
                            print("***SHIFTED Maintenance Date: "+str(shifted_maintenance_date))
                        if forecast_response.status_code != status.HTTP_200_OK:
                            return forecast_response
                        
                        ##### Send Due Soon Emails:
                        all_managers = list(UserHelper.get_all_managers(db_name).values_list('detailed_user_id', 'email'))
                        user_location_list = list(UserHelper.get_user_location_table(db_name).values_list('detaileduser_id', 'locationmodel_id'))
                        locations = HelperMethods.extract_tuple_list_from_tuple_list(shifted_due_soon_list, [2, 3])
                        unique_locations = [t for t in (set(tuple(i) for i in locations))]
                        #TODO
                        # create new email templ;ates for overdue for all 3 systems
                        maintenance_forecast_template_string = PdfManager.read_template_file(PdfManager.template_dict.get('maintenance_forecast_notification_template'))
                        row_template_string = PdfManager.read_template_file(PdfManager.template_dict.get('maintenance_forecast_notification_row_template'))

                        print("-----------------------------------------")
                        for location in unique_locations:
                            location_id = location[0]
                            location_name = location[1]
                            location_inrange_rules = [x for x in shifted_due_soon_list if x[2] == location_id]
                            # -------------- Email maintenance notifications ---------------
                            emails = WebJobHelper.get_manager_emails_from_tuple_lists_for_location(all_managers, user_location_list, location_id)
                            if len(emails) > 0:
                                print("Sending PM DUE SOON Notification for location(" + str(location_id) + "): " + str(location_name))
                                notification_config, resp = NotificationHelper.get_notification_config_by_name("Maintenance Forecast", db_name)
                                if resp.status_code != status.HTTP_302_FOUND:
                                    return resp
                                if notification_config.active and (
                                    notification_config.triggers is None or (
                                        "notify_overdue_maintenance" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                                    )
                                ):
                                    html_email = PdfManager.gen_daily_maintenance_notification_email(  #TODO - have to make one for overdue version as well
                                        day_start.date(),
                                        day_end.date(),
                                        location_inrange_rules,
                                        notification_config,
                                        db_name,
                                        maintenance_forecast_template_string=maintenance_forecast_template_string,
                                        row_template_string=row_template_string
                                    )

                                    if notification_config.recipient_type == "auto":
                                        recipients = emails
                                    else:
                                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, db_name)

                                    email_title = str(location_name) + " - Maintenance Forecasted For: " + str(day_start.date()) + " to " + str(day_end.date())  #TODO email title
                                    email_response = Email.send_email_notification(emails, email_title, html_email, [], html_content=True)
                                    if email_response.status_code != status.HTTP_200_OK:
                                        print("Email failed")
                        
                        ##### Send OVERDUE Emails:
                        all_managers = list(UserHelper.get_all_managers(db_name).values_list('detailed_user_id', 'email'))
                        user_location_list = list(UserHelper.get_user_location_table(db_name).values_list('detaileduser_id', 'locationmodel_id'))
                        locations = HelperMethods.extract_tuple_list_from_tuple_list(shifted_overdue_list, [2, 3])
                        unique_locations = [t for t in (set(tuple(i) for i in locations))]
                        #TODO
                        # create new email templ;ates for overdue for all 3 systems
                        maintenance_forecast_template_string = PdfManager.read_template_file(PdfManager.template_dict.get('maintenance_forecast_overdue_notification_template'))
                        row_template_string = PdfManager.read_template_file(PdfManager.template_dict.get('maintenance_forecast_overdue_notification_row_template'))

                        print("-----------------------------------------")
                        for location in unique_locations:
                            location_id = location[0]
                            location_name = location[1]
                            location_inrange_rules = [x for x in shifted_overdue_list if x[2] == location_id]
                            # -------------- Email maintenance notifications ---------------
                            emails = WebJobHelper.get_manager_emails_from_tuple_lists_for_location(all_managers, user_location_list, location_id)
                            if len(emails) > 0:
                                print("Sending PM OVERDUE Notification for location(" + str(location_id) + "): " + str(location_name))
                                notification_config, resp = NotificationHelper.get_notification_config_by_name("Overdue Maintenance", db_name)
                                if resp.status_code != status.HTTP_302_FOUND:
                                    return resp

                                if notification_config.active and (
                                    notification_config.triggers is None or (
                                        "notify_overdue_maintenance" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                                    )
                                ):
                                    html_email = PdfManager.gen_daily_maintenance_overdue_notification_email(  #TODO - have to make one for overdue version as well
                                        location_inrange_rules,
                                        notification_config,
                                        db_name,
                                        maintenance_forecast_template_string=maintenance_forecast_template_string,
                                        row_template_string=row_template_string
                                    )

                                    if notification_config.recipient_type == "auto":
                                        recipients = emails
                                    else:
                                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, db_name)

                                    email_title = "Maintenance Overdue Alert"  #TODO email title
                                    # email_title = str(location_name) + " - Maintenance Forecasted For: " + str(day_start.date()) + " to " + str(day_end.date())
                                    email_response = Email.send_email_notification(recipients, email_title, html_email, [], html_content=True)
                                    if email_response.status_code != status.HTTP_200_OK:
                                        print("Email failed")

                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.NF_0, e))
                        print(CustomError.get_error_dev(CustomError.NF_0, e))

            return Response(status=status.HTTP_200_OK)
          
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_notify_expiry():
        try:
            database_names = list(settings.DATABASES.keys())
            for db_name in database_names:
                dbs_to_skip = ['auth_db', 'payment', 'default']
                if db_name not in dbs_to_skip:
                    try:
                        print("**********************************************************************************")
                        print("Processing expiry notifications for database " + str(db_name) + ":")

                        week_start, week_end = HelperMethods.get_datetime_range_for_this_week()
                        # NOTE: Uncomment two lines below to test
                        # week_start = HelperMethods.datetime_string_to_datetime("2000-02-02 00:00:00.000000")
                        # week_end = HelperMethods.datetime_string_to_datetime("2028-02-02 00:00:00.000000")

                        all_locations = LocationHelper.get_all_locations(db_name).values('location_id', 'location_name')
                        all_managers = list(UserHelper.get_all_managers(db_name).values_list('detailed_user_id', 'email'))
                        user_location_list = list(UserHelper.get_user_location_table(db_name).values_list('detaileduser_id', 'locationmodel_id'))
                        asset_files = AssetHelper.get_all_asset_files(db_name).exclude(expiration_date=None).values_list(
                        'expiration_date', 'file_purpose', 'VIN', 'VIN__current_location')

                        expiry_notification_template_string = PdfManager.read_template_file(PdfManager.template_dict.get('expiry_notification_template'))
                        row_template_string = PdfManager.read_template_file(PdfManager.template_dict.get('expiry_notification_row_template'))

                        for location in all_locations:
                            location_id = location.get('location_id')
                            location_name = location.get('location_name')
                            print("#########################")
                            print(str(location_name) + " - " + str(location_id))
                            location_dict = {}
                            file_subset = ChartCalculationsHelper.get_subset_for_int_field(location.get('location_id'), asset_files, field_index=3)
                            for file in file_subset:
                                expiry_date = file[0]
                                file_purpose = file[1]
                                vin = file[2]

                                if HelperMethods.date_in_range(expiry_date, week_start, week_end):
                                    if vin not in location_dict:
                                        location_dict[vin] = []
                                    if file_purpose not in location_dict[vin]:
                                        print("VIN: " + str(vin) + " // " + "File Purpose: " + str(file_purpose) + " // " + "Expiry Date: " + str(expiry_date))
                                        print("In range and not already listed ---> Adding to expiring items.")
                                        print("-----------------")
                                        location_dict[vin].append(file_purpose)
                                        location_dict[vin] = sorted(location_dict.get(vin))

                            if len(location_dict) > 0:
                                # -------------- Email expiry notifications ---------------
                                print("Sending Expiry Notification for location(" + str(location_id) + "): " + str(location_name))
                                emails = WebJobHelper.get_manager_emails_from_tuple_lists_for_location(all_managers, user_location_list, location_id)
                                if len(emails):
                                    notification_config, resp = NotificationHelper.get_notification_config_by_name("Expiry", db_name)
                                    if resp.status_code != status.HTTP_302_FOUND:
                                        return resp
                                    if notification_config.active and (
                                        notification_config.triggers is None or (
                                            "notify_expiry" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                                        )
                                    ):
                                        html_email = PdfManager.gen_expiry_notification_email(
                                            week_start.date(),
                                            week_end.date(),
                                            location_dict,
                                            notification_config,
                                            db_name,
                                            expiry_notification_template_string=expiry_notification_template_string,
                                            row_template_string=row_template_string
                                        )

                                        if notification_config.recipient_type == "auto":
                                            recipients = emails
                                        else:
                                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, db_name)

                                        email_title = str(location_name) + " - Expiry Notification For: " + str(week_start.date()) + " to " + str(week_end.date())
                                        email_response = Email.send_email_notification(recipients, email_title, html_email, [], html_content=True)
                                        if email_response.status_code != status.HTTP_200_OK:
                                            print("Email failed")

                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.NF_1, e))
                        print(CustomError.get_error_dev(CustomError.NF_1, e))

            return Response(status=status.HTTP_200_OK)
          
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_receive_messages():
        try:
            client = 'WestJet'
            company_name = client
            connection_string = settings.SERVICE_BUS_LISTEN_TOPIC_CONNECTION_DETAILS.get(client).get("primary_connection_string")
            subscription_name = settings.SERVICE_BUS_LISTEN_TOPIC_CONNECTION_DETAILS.get(client).get("subscription_name")
            topic_name = settings.SERVICE_BUS_LISTEN_TOPIC_CONNECTION_DETAILS.get(client).get("topic_name")
            servicebus_client = ServiceBusClient.from_connection_string(conn_str=connection_string, logging_enable=True)
            with servicebus_client:
                # Get the topic receiver object
                receiver = servicebus_client.get_subscription_receiver(
                                            subscription_name=subscription_name,
                                            topic_name=topic_name,
                                            max_wait_time=5)

                messages = {}
                count = 0
                history_func = lambda : True
                channel_name = company_name
                with receiver:
                    for msg in receiver:
                        print("getting msg")
                        print("Receiving: {}".format(msg))
                        print("Message ID: {}".format(msg.message_id))
                        messages['Message ' + str(count)] = "{}".format(msg)
                        count += 1
                        pusher_payload = "{}".format(msg)
                        pusher_helper = PusherHelper(channel_name, PusherHelper.ASBMessageReceived, pusher_payload, False, history_func)
                        pusher_helper.push_chunked()
                        print("pusher done")
                        receiver.complete_message(msg)

            return Response(messages, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
