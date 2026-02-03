from api.Models.Cost.currency import Currency
from rest_framework.response import Response
from rest_framework import status
from api.Models.Snapshot.snapshot_daily_asset import SnapshotDailyAsset
from api.Models.Snapshot.snapshot_daily_location_cost import SnapshotDailyLocationCost
from api.Models.Snapshot.snapshot_daily_counts import SnapshotDailyCounts
from api.Models.Snapshot.snapshot_daily_location_counts import SnapshotDailyLocationCounts
from api.Models.Snapshot.snapshot_daily_currency import SnapshotDailyCurrency
from core.CurrencyManager.CurrencyHelper import CurrencyHelper
from .SnapshotHelper import SnapshotDailyCurrencyHelper
from ..Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
import datetime

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class SnapshotDailyFleetUpdater():

    @staticmethod
    def create_snapshot_daily_asset_entry(asset):
        return SnapshotDailyAsset(
            VIN=asset.get("VIN"),
            parent=asset.get("parent"),
            equipment_type=asset.get("equipment_type"),
            company=asset.get("company"),
            jde_department=asset.get("jde_department"),
            original_location=asset.get("original_location"),
            current_location=asset.get("current_location"),
            status=asset.get("status"),
            aircraft_compatability=asset.get("aircraft_compatability"),
            unit_number=asset.get("unit_number"),
            license_plate=asset.get("license_plate"),
            date_of_manufacture=asset.get("date_of_manufacture"),
            department=asset.get("department"),
            job_specification=asset.get("job_specification"),
            fire_extinguisher_quantity=asset.get("fire_extinguisher_quantity"),
            fire_extinguisher_inspection_date=asset.get("fire_extinguisher_inspection_date"),
            path=asset.get("path"),
            last_process=asset.get("last_process"),
            hours_or_mileage=asset.get("hours_or_mileage"),
            mileage=asset.get("mileage"),
            hours=asset.get("hours"),
            mileage_unit=asset.get("mileage_unit"),
            date_in_service=asset.get("date_in_service"),
            total_cost=asset.get("total_cost"),
            currency=asset.get("currency"),
            daily_average_hours=asset.get("daily_average_hours"),
            daily_average_mileage=asset.get("daily_average_mileage"),
            replacement_hours=asset.get("replacement_hours"),
            replacement_mileage=asset.get("replacement_mileage"),
            insurance_renewal_date=asset.get("insurance_renewal_date"),
            registration_renewal_date=asset.get("registration_renewal_date"),
            load_capacity=asset.get("load_capacity"),
            load_capacity_unit=asset.get("load_capacity_unit"),
            fuel=asset.get("fuel"),
            engine=asset.get("engine"),
            colour=asset.get("colour"),
            fuel_tank_capacity=asset.get("fuel_tank_capacity"),
            fuel_tank_capacity_unit=asset.get("fuel_tank_capacity_unit"),
            is_rental=asset.get("is_rental"),
            monthly_subscription_cost=asset.get("monthly_subscription_cost")
        )

class SnapshotDailyCostUpdater():

    @staticmethod
    def create_snapshot_cost_daily_entry(daily_cost_dict):
        return SnapshotDailyLocationCost(
            location=daily_cost_dict.get('location'),
            volume_fuel=daily_cost_dict.get('volume_fuel'),
            volume_unit=daily_cost_dict.get('volume_unit'),
            total_cost_fuel=daily_cost_dict.get('total_cost_fuel'),
            taxes_fuel=daily_cost_dict.get('taxes_fuel'),
            deductible=daily_cost_dict.get('deductible'),
            total_cost_insurance=daily_cost_dict.get('total_cost_insurance'),
            total_base_hours=daily_cost_dict.get('total_base_hours'),
            total_overtime_hours=daily_cost_dict.get('total_overtime_hours'),
            total_cost_labor=daily_cost_dict.get('total_cost_labor'),
            taxes_labor=daily_cost_dict.get('taxes_labor'),
            license_registration_cost=daily_cost_dict.get('license_registration_cost'),
            license_plate_renewal_cost=daily_cost_dict.get('license_plate_renewal_cost'),
            total_cost_license=daily_cost_dict.get('total_cost_license'),
            taxes_license=daily_cost_dict.get('taxes_license'),
            total_cost_parts=daily_cost_dict.get('total_cost_parts'),
            taxes_parts=daily_cost_dict.get('taxes_parts'),
            total_cost_rental=daily_cost_dict.get('total_cost_rental'),
            total_cost_acquisition=daily_cost_dict.get('total_cost_acquisition'),
            taxes_acquisition=daily_cost_dict.get('taxes_acquisition'),
            total_cost_delivery=daily_cost_dict.get('total_cost_delivery'),
            taxes_delivery=daily_cost_dict.get('taxes_delivery'),
            currency=daily_cost_dict.get('currency')
        )

class SnapshotDailyCountsUpdater():

    @staticmethod
    def create_snapshot_daily_counts(daily_counts_dict, db_name):
        return SnapshotDailyCounts.objects.using(db_name).create(
            asset_count=daily_counts_dict.get("asset_count"),
            user_count=daily_counts_dict.get("user_count")
            )

    @staticmethod
    def create_snapshot_daily_location_counts(daily_location_count, db_name):
        return SnapshotDailyLocationCounts(
                all_asset_count = daily_location_count.get("all_asset_count"),
                active_asset_count = daily_location_count.get("active_asset_count"),
                daily_check_count = daily_location_count.get("daily_check_count"),
                location = daily_location_count.get("location"),
                date_of_checks = daily_location_count.get("date_of_checks"))

class SnapshotDailyCurrencyUpdater():

    @staticmethod
    def create_snapshot_daily_currency(daily_currency_dict, db_name):
        return SnapshotDailyCurrency(
            currency = daily_currency_dict.get("currency"),
            currency_value = daily_currency_dict.get("currency_value")
        )

    #this method will either create or update each currency for the snapshot table based on the currency table
    @staticmethod
    def update_snapshot_currencies(rates_json, standard_currency_code, db_name):
        try:
            standard_value = rates_json[standard_currency_code] if standard_currency_code is not None else 'USD'
            # logic: we have two lists - one for the currencies snapshots that aren't created yet, and one for ones that 
            # need to be updated with newest rates - so that the snapshot currencies are properly updated if the currency
            # table changes
            create_exchange_entries = []
            update_exchange_entries = []
            currencies = CurrencyHelper.get_list_currencies(db_name)

            for currency in currencies:
                snapshot_obj_list = SnapshotDailyCurrency.objects.using(db_name).filter(currency=currency.id)
                # api returns values in EURO, i.e. 1.2 USD/EURO. So to get standard currency to 1 (and do proper conversion), we divide every
                # currency rate by the value of the standard_currency
                if len(snapshot_obj_list) == 0: #means that the currency does not exist in snapshot yet
                    entry = SnapshotDailyCurrencyUpdater.create_snapshot_daily_currency(
                        {"currency": currency, "currency_value": rates_json[currency.code] / standard_value }, 
                        db_name)
                    create_exchange_entries.append(entry)
                else: # currency exists in snapshot, we just need to update the row
                    update_exchange_entries.append(snapshot_obj_list[0])
                    snapshot_obj_list[0].currency_value = rates_json[currency.code] / standard_value
                    snapshot_obj_list[0].date_modified = HelperMethods.naive_to_aware_utc_datetime(datetime.datetime.utcnow())
            
            SnapshotDailyCurrency.objects.using(db_name).bulk_create(create_exchange_entries)
            SnapshotDailyCurrency.objects.using(db_name).bulk_update(update_exchange_entries, ['currency_value', 'date_modified'])

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)