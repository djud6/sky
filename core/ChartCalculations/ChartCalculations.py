from api.Models.fuel_type import FuelType
from api.Models.repairs import RepairsModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.Snapshot.snapshot_daily_location_counts import SnapshotDailyLocationCounts
from core.CostManager.CostHelper import DeliveryHelper, InsuranceHelper, LaborHelper, PartsHelper, RentalHelper
from .ChartCalculationsHelper import ChartCalculationsHelper
from ..Helper import HelperMethods
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from ..LocationManager.LocationHelper import LocationHelper
from ..RepairManager.RepairHelper import RepairHelper
from ..MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from ..AccidentManager.AccidentHelper import AccidentHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..IssueManager.IssueHelper import IssueHelper
from ..UserManager.UserHelper import UserHelper
from api.Models.asset_model import AssetModel
from api.Models.asset_model_history import AssetModelHistory
from api.Models.equipment_type import EquipmentTypeModel
from api.Models.Snapshot.snapshot_daily_location_cost import SnapshotDailyLocationCost
from api.Models.Snapshot.snapshot_daily_asset import SnapshotDailyAsset
from api.Models.asset_daily_checks import AssetDailyChecksModel
from api.Models.Cost.fuel_cost import FuelCost
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from GSE_Backend.errors.ErrorDictionary import CustomError
from datetime import date, datetime, timedelta
from django.db.models import Avg, ExpressionWrapper, F, DurationField
import logging
from django.utils import timezone
import calendar
from collections import defaultdict
import traceback
from django.db.models import Sum
import datetime
from dateutil.relativedelta import relativedelta

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ChartCalculations:

    @staticmethod
    def get_asset_status_breakdown(user):
    # process_choices = [(Repair, "Repair"), (Accident, "Accident"), (Disposal, "Disposal"), (Maintenance, "Preventitive Maintenance"), (Null, None)]
        active = 0
        repairs = 0
        accidents = 0
        disposal = 0
        maintenance = 0
        status_process_pairs = AssetHelper.filter_assets_for_user(AssetHelper.get_all_assets(user.db_access).values_list('status', 'last_process'), user)
        for pair in status_process_pairs:
            if pair[0].lower() == AssetModel.Active.lower():
                active += 1
            else:
                if pair[1].lower() == AssetModel.Repair.lower():
                    repairs += 1
                if pair[1].lower() == AssetModel.Accident.lower():
                    accidents += 1
                if pair[1].lower() == AssetModel.Disposal.lower():
                    disposal += 1
                if pair[1].lower() == AssetModel.Maintenance.lower():
                    maintenance += 1

        return {"active_num": active, "repairs_num": repairs, "maintenance_num": maintenance, "incident_num": accidents, "disposal_num": disposal}

    #---------------------------------------------------------------------------------------------------

    # For the last 3 months
    @staticmethod
    def get_asset_process_breakdown(user):
        db_name = user.db_access
        start_date = HelperMethods.subtract_time_from_datetime(datetime.datetime.now(datetime.timezone.utc), 92, time_unit="days").replace(tzinfo=timezone.utc)
        location_tuples = LocationHelper.get_all_locations(db_name).values_list('location_id', 'location_name')
        all_repairs = list(RepairHelper.get_repairs_after_date(start_date, db_name).exclude(location=None).values_list('location', 'status'))
        all_maintenance = list(MaintenanceHelper.get_maintenance_after_date(start_date, db_name).exclude(location=None).values_list('location', 'status'))
        all_accidents = list(AccidentHelper.get_accidents_after_date(start_date, db_name).exclude(location=None).values_list('location', 'is_resolved'))

        locations_json_array = []

        for location in location_tuples:
            location_id = location[0]
            location_name = location[1]

            repairs_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_repairs)
            repair_complete_count, repair_incomplete_count = ChartCalculationsHelper.get_complete_and_incomplete_counts_for_process(RepairsModel.complete ,repairs_subset, status_index=1)

            maintenance_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_maintenance)
            maintenance_complete_count, maintenance_incomplete_count = ChartCalculationsHelper.get_complete_and_incomplete_counts_for_process(MaintenanceRequestModel.complete, maintenance_subset, status_index=1)

            accidents_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_accidents)
            accident_complete_count, accident_incomplete_count = ChartCalculationsHelper.get_complete_and_incomplete_counts_for_process(True, accidents_subset, status_index=1)

            location_data = {
                "complete_repairs":repair_complete_count,
                "complete_repairs_percentage": (repair_complete_count / len(repairs_subset)) * 100 if repairs_subset else 0,
                "incomplete_repairs":repair_incomplete_count,
                "incomplete_repairs_percentage": (repair_incomplete_count / len(repairs_subset)) * 100 if repairs_subset else 0,
                "complete_maintenance":maintenance_complete_count,
                "complete_maintenance_percentage": (maintenance_complete_count / len(maintenance_subset)) * 100 if maintenance_subset else 0,
                "incomplete_maintenance":maintenance_incomplete_count,
                "incomplete_maintenance_percentage": (maintenance_incomplete_count / len(maintenance_subset)) * 100 if maintenance_subset else 0,
                "complete_accidents":accident_complete_count,
                "complete_accidents_percentage":  (accident_complete_count / len(accidents_subset)) * 100 if accidents_subset else 0,
                "incomplete_accidents":accident_incomplete_count,
                "incomplete_accidents_percentage": (accident_incomplete_count / len(accidents_subset)) * 100 if accidents_subset else 0
            }

            location_wrapper = {location_name:location_data}

            locations_json_array.append(location_wrapper)

        return locations_json_array

    #---------------------------------------------------------------------------------------------------


    @staticmethod
    def get_assets_and_operators_count_per_location(user):
        db_name = user.db_access
        location_tuples = LocationHelper.get_all_locations(db_name).values_list('location_id', 'location_name', 'latitude', 'longitude')
        all_asset_locations = list(AssetHelper.get_all_assets(db_name).values_list('current_location', flat=True))
        all_operators = list(UserHelper.get_all_operators(db_name).values_list('detailed_user_id', flat=True))
        users_locations = list(UserHelper.get_user_location_table(db_name).values_list('detaileduser_id', 'locationmodel_id'))

        locations_info = []

        for loc_id_name_tuple in location_tuples:
            location_id = loc_id_name_tuple[0]
            location_name = loc_id_name_tuple[1]
            latitude = loc_id_name_tuple[2]
            longitude = loc_id_name_tuple[3]
            
            total_ops = 0
            for user_location_tuple in users_locations:
                if user_location_tuple[0] == location_id:
                    if user_location_tuple[1] in all_operators:
                        total_ops += 1

            total_assets = 0
            for asset_location in all_asset_locations:
                if asset_location == location_id:
                    total_assets += 1
            
            location_json = {location_name:{"latitude": latitude, "longitude":longitude, "operators":total_ops, "assets":total_assets}}
            locations_info.append(location_json)

        return locations_info

    #---------------------------------------------------------------------------------------------------

    # For last 3 months
    @staticmethod
    def get_asset_performance_leaderboard(user):
        db_name = user.db_access
        all_issue_vins = list(IssueHelper.get_all_issues_in_last_x_days(days=92, db_name=db_name).values_list('VIN', flat=True))
        all_tracked_assets = list(AssetHelper.get_all_tracked_assets(db_name).values_list('VIN', 'equipment_type__asset_type__name','unit_number'))
        all_asset_types = list(AssetTypeHelper.get_all_asset_types(db_name).values_list('name', flat=True))

        asset_types_performance_list = []

        for asset_type in all_asset_types:
            vin_issue_count_tuple_list = [] # will store (vin, issue_count) tuples in list in order to sort
            for asset in all_tracked_assets:
                issue_count = 0
                cur_vin = asset[0]
                cur_type = asset[1]
                cur_unit = asset[2]
                if cur_type == asset_type:
                    issue_count += all_issue_vins.count(cur_vin) # Add count of all occurances of vin in all_issue_vins
                    vin_issue_count_tuple_list.append((cur_vin, issue_count, cur_unit))

            vin_issue_count_tuple_list = sorted(vin_issue_count_tuple_list, key=lambda x: x[1]) # Sort the tuple list (from least issues to most)
            #vin_list, count_list = zip(*vin_issue_count_tuple_list)

            asset_type_json = {asset_type: vin_issue_count_tuple_list}
            asset_types_performance_list.append(asset_type_json)

        return asset_types_performance_list

    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_location_asset_types(user):
        db_name = user.db_access
        locations = list(LocationHelper.get_all_locations(db_name).values_list('location_id', 'location_name'))
        all_assets = list(AssetHelper.get_all_assets(db_name).values_list('current_location', 'equipment_type__asset_type__name'))

        locations_and_their_types = []
        for location_tuple in locations:
            location_id = location_tuple[0]
            location_name = location_tuple[1]
            assets_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_assets)

            types_and_counts = []
            if len(assets_subset) > 0:
                cur_locations, asset_types = zip(*assets_subset)
                previously_counted_types = []
                for asset_tuple in assets_subset:
                    current_location = asset_tuple[0]
                    asset_type = asset_tuple[1]
                    if current_location == location_id:
                        if asset_type not in previously_counted_types:
                            type_count = asset_types.count(asset_type)
                            previously_counted_types.append(asset_type)
                            types_and_counts.append((asset_type, type_count))

            location_types_json = {location_name: types_and_counts}
            locations_and_their_types.append(location_types_json)

        return locations_and_their_types

    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_location_maintenance_downtime_average(user):
        db_name = user.db_access
        start_date = HelperMethods.subtract_time_from_datetime(datetime.datetime.now(datetime.timezone.utc), 92, time_unit="days").replace(tzinfo=timezone.utc)
        locations = list(LocationHelper.get_all_locations(db_name).values_list('location_id', 'location_name'))
        all_maintenance = list(MaintenanceHelper.get_maintenance_after_date(start_date, db_name).values_list('location', 'available_pickup_date', 'date_completed'))

        locations_downtime_averages = []
        for location in locations:
            location_id = location[0]
            location_name = location[1]

            maintenance_for_location = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_maintenance)
            downtimes_for_location = []
            for maintenance in maintenance_for_location:
                pick_up_date = maintenance[1]
                if pick_up_date is None:
                    continue # If no pickup date then don't calc dt for this maintenance
                date_completed = maintenance[2]
                if date_completed is None or str(date_completed) == "":
                    date_completed = datetime.datetime.now(datetime.timezone.utc)

                downtime = HelperMethods.get_datetime_delta(pick_up_date, date_completed, delta_format="hours")
                downtimes_for_location.append(downtime)

            if len(downtimes_for_location) > 0:
                average_downtime_for_loc = sum(downtimes_for_location) / len(downtimes_for_location)
            else:
                average_downtime_for_loc = 0

            location_downtime_json = {location_name: average_downtime_for_loc}
            locations_downtime_averages.append(location_downtime_json)
        
        return locations_downtime_averages

    #---------------------------------------------------------------------------------------------------
    
    @staticmethod
    def total_maintenance_hours(start_date, end_date, user):
        db_name = user.db_access
        all_maintenance = MaintenanceRequestModel.objects.filter(date_created__range=[start_date, end_date]).using(db_name)
        
        total_hours = 0
        for maintenance in all_maintenance:
            pick_up_date = maintenance.available_pickup_date
            date_completed = maintenance.date_completed

            if pick_up_date:
                if date_completed:
                    downtime = HelperMethods.get_datetime_delta(pick_up_date, date_completed, delta_format="hours")
                    total_hours += downtime

        return abs(total_hours)
    
    # ---------------------------------------------------------------------------------------------------

    @staticmethod
    def total_repair_hours(start_date, end_date, user):
        db_name = user.db_access
        all_repairs = RepairsModel.objects.filter(date_created__range=[start_date, end_date]).using(db_name)

        total_hours = 0
        for repair in all_repairs:
            available_pickup_date = repair.available_pickup_date
            date_completed = repair.date_completed

            if available_pickup_date and date_completed:
                repair_hours = HelperMethods.get_datetime_delta(available_pickup_date, date_completed, delta_format="hours")
                total_hours += repair_hours

        return abs(total_hours)
    
    @staticmethod
    def get_fleet_usage_volume(user):
        db_name = user.db_access
        locations = list(LocationHelper.get_all_locations(db_name).values_list('location_id', 'location_name'))
        fuel_types = FuelType.objects.using(db_name).values_list('id','name')
        all_fuel_costs = list(FuelCost.objects.using(db_name).values_list('location_id','date_created','volume','volume_unit','fuel_type_id').order_by('fuel_type_id','location_id','date_created'))

        combined_similar_assets = ChartCalculationsHelper.combine_similar(all_fuel_costs)

        locations_and_fuel_type = []
        for fuel_tuple in fuel_types:
            fuel_id = fuel_tuple[0]
            fuel_name = fuel_tuple[1]
            locations_and_their_fuel_volume = []
            for location_tuple in locations:
                location_id = location_tuple[0]
                location_name = location_tuple[1]
                assets_subset = ChartCalculationsHelper.get_subset_for_int_field(location_id, combined_similar_assets)
                date_and_volume = []
                if len(assets_subset) > 0:
                    for asset_tuple in assets_subset:
                        current_location = asset_tuple[0] or -1
                        fuel_use = asset_tuple[2]
                        date = asset_tuple[1]
                        unit = asset_tuple[3]
                        fuel_type = asset_tuple[4] or -1
                        if int(current_location) == int(location_id) and int(fuel_type) == int(fuel_id):
                            if(unit == "liter"):
                                date_and_volume.append((date,{"liters:": fuel_use},{"gallons:": fuel_use*0.264172}))
                            elif(unit == "gallon"):   
                                date_and_volume.append((date,{"liters:": fuel_use*3.78541},{"gallons:": fuel_use}))
                            elif(unit == "kWh"):
                                date_and_volume.append((date,{"kWh:": fuel_use}))
                            elif(unit == "lb"):
                                date_and_volume.append((date,{"kg:": fuel_use*2.20462},{"lb:": fuel_use}))
                            elif(unit == "kg"):
                                date_and_volume.append((date,{"kg:": fuel_use},{"lb:": fuel_use*0.453592}))
                            elif(unit == "SCM"):
                                date_and_volume.append((date,{"SCM:": fuel_use},{"SCF:": fuel_use*35.3147}))
                            elif(unit == "SCF"):
                                date_and_volume.append((date,{"SCM:": fuel_use*0.0283168},{"SCF:": fuel_use}))

                location_types_json = {location_name: date_and_volume}
                locations_and_their_fuel_volume.append(location_types_json)
            locations_and_fuel_type_json = {fuel_name:locations_and_their_fuel_volume}
            locations_and_fuel_type.append(locations_and_fuel_type_json)
        return locations_and_fuel_type

    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_fuel_cost(user, _time_unit):
        db_name = user.db_access
        location_info = []

        locations = LocationHelper.get_all_locations(db_name).values()
        location_cost_snapshots = SnapshotDailyLocationCost.objects.using(db_name).order_by('location',
                                                                                            'date_created').values()
        for location in locations:
            fuel_cost_by_location = []

            for location_snap in location_cost_snapshots:
                # TODO: in SnapshotDailyLocationCost model, location isn't an FK of location, but a simple varchar.
                #  This needs to be checked with someone... is that intentional or a mistake?
                if location_snap['location'] == str(location['location_id']):
                    fuel_cost_by_location.append(location_snap)
                elif len(fuel_cost_by_location) > 0:
                    # Since the user_locs is ordered by location, we can break the loop as soon as the list has items
                    # and a different location from location_id is found. This break only purpose is optimization!
                    # Everything should behave as expected without it, but a bit slower.
                    break

            location_info.append({
                location['location_name']: ChartCalculationsHelper.calculate_location_fuel_cost(fuel_cost_by_location,
                                                                                                _time_unit)})

        return location_info
             
    #---------------------------------------------------------------------------------------------------
    
    @staticmethod
    def get_daily_checks_and_assets(user):
      
        # build map of location names by id for quick lookup
        
        locations=LocationHelper.get_all_locations(user.db_access).all()
        locations_by_id={}
        for row in locations:
            locations_by_id[row.location_id]=row.location_name
        
        # two values sum to the total active asset count per location (names a bit misleading now...)
        
        stats_by_location={}
        for value in locations_by_id.values():
            stats_by_location[value]={
                "asset_count":0,
                "daily_check_count":0
            }
        
        assets_list=AssetHelper.get_assets_not_in_VIN_list_and_active([],user.db_access).values("current_location")
        for row in assets_list:
            location_pretty=locations_by_id[row.get("current_location")]
            stats_by_location[location_pretty]["asset_count"]+=1
        
        now=timezone.now()
        
        checks_list=AssetDailyChecksModel.objects.using(user.db_access).filter(
            date_created__year=now.year,
            date_created__month=now.month,
            date_created__day=now.day
        ).values("location")
        for row in checks_list:
            location_pretty=locations_by_id[row.get("location")]
            stats_by_location[location_pretty]["asset_count"]-=1
            stats_by_location[location_pretty]["daily_check_count"]+=1
        
        # hack so the data structure is the same and FE map/reduce doesn't need any changes (but arrays always have 1 item now)

        stats_compatible=[]
        for location,stats in stats_by_location.items():
            stats_compatible.append({
                location:[
                    stats
                ]
            })
        return stats_compatible
             
    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_fleet_usage_datetime(user, start_date, end_date):
        start_date = timezone.make_aware(timezone.datetime.strptime(start_date, "%Y-%m-%d"))
        end_date = timezone.make_aware(timezone.datetime.strptime(end_date, "%Y-%m-%d"))

        fleet_earliest_date = timezone.now()
        fleet_earliest_date = fleet_earliest_date.replace(year=fleet_earliest_date.year - 1)

        # In case it's a leap year
        fleet_earliest_date = fleet_earliest_date.replace(day=28 if (fleet_earliest_date.month == 2 and fleet_earliest_date.day == 29) else fleet_earliest_date.day)

        # Yearly average usage
        all_mileage_usage = SnapshotDailyAsset.objects.using(user.db_access).exclude(hours_or_mileage="Hours").exclude(hours_or_mileage="Neither").filter(date_created__range=[start_date, end_date]).values_list('daily_average_mileage', 'date_created').order_by('date_created')
        all_hour_usage = SnapshotDailyAsset.objects.using(user.db_access).exclude(hours_or_mileage="Mileage").exclude(hours_or_mileage="Neither").filter(date_created__range=[start_date, end_date]).values_list('daily_average_hours', 'date_created').order_by('date_created')

        yearly_mileage = {"yearly_average_per_asset": 0.0}
        daily_mileage = {"daily_averages": [{"date": "", "daily_average_per_asset": 0.0}]}
        weekly_mileage = {"weekly_averages": [{"start_date": "", "end_date": "", "weekly_average_per_asset": 0.0}]}
        monthly_mileage = {"monthly_averages": [{"month": "", "monthly_average_per_asset": 0.0}]}

        yearly_hours = {"yearly_average_per_asset": 0.0}
        daily_hours = {"daily_averages": [{"date": "", "daily_average_per_asset": 0.0}]}
        weekly_hours = {"weekly_averages": [{"start_date": "", "end_date": "", "weekly_average_per_asset": 0.0}]}
        monthly_hours = {"monthly_averages": [{"month": "", "monthly_average_per_asset": 0.0}]}

        if len(all_mileage_usage) > 0:
            # Calculate yearly average for mileage
            total_mileage = sum(mileage for mileage, _ in all_mileage_usage)
            yearly_mileage = {"yearly_average_per_asset": total_mileage / len(all_mileage_usage)}

            # Calculate daily averages for mileage
            daily_mileage = {"daily_averages": [{"date": date_created.strftime("%Y-%m-%d"), "daily_average_per_asset": mileage} for mileage, date_created in all_mileage_usage]}

            # Calculate weekly averages for mileage
            weekly_mileage = {"weekly_averages": []}
            current_week_start = None
            current_week_end = None
            weekly_data = []

            for mileage, date_created in all_mileage_usage:
                if current_week_start is None:
                    current_week_start = date_created.date()
                    current_week_end = current_week_start + datetime.timedelta(days=6)
                elif date_created.date() > current_week_end:
                    weekly_average = sum(weekly_data) / len(weekly_data)
                    weekly_mileage["weekly_averages"].append({
                        "start_date": current_week_start.strftime("%Y-%m-%d"),
                        "end_date": current_week_end.strftime("%Y-%m-%d"),
                        "weekly_average_per_asset": weekly_average
                    })
                    current_week_start += datetime.timedelta(days=7)
                    current_week_end = current_week_start + datetime.timedelta(days=6)
                    weekly_data = []

                weekly_data.append(mileage)

            if weekly_data:
                weekly_average = sum(weekly_data) / len(weekly_data)
                weekly_mileage["weekly_averages"].append({
                    "start_date": current_week_start.strftime("%Y-%m-%d"),
                    "end_date": current_week_end.strftime("%Y-%m-%d"),
                    "weekly_average_per_asset": weekly_average
                })

            # Calculate monthly averages for mileage
            monthly_mileage = {"monthly_averages": []}
            current_month = None
            monthly_data = []

            for mileage, date_created in all_mileage_usage:
                if current_month is None:
                    current_month = date_created.date().replace(day=1)
                elif date_created.date().replace(day=1) != current_month:
                    monthly_average = sum(monthly_data) / len(monthly_data)
                    monthly_mileage["monthly_averages"].append({
                        "month": current_month.strftime("%Y-%m"),
                        "monthly_average_per_asset": monthly_average
                    })
                    current_month += relativedelta(months=1)
                    monthly_data = []

                monthly_data.append(mileage)

            if monthly_data:
                monthly_average = sum(monthly_data) / len(monthly_data)
                monthly_mileage["monthly_averages"].append({
                    "month": current_month.strftime("%Y-%m"),
                    "monthly_average_per_asset": monthly_average
                })

        if len(all_hour_usage) > 0:
            # Calculate yearly average for hours
            total_hours = sum(hours for hours, _ in all_hour_usage)
            yearly_hours = {"yearly_average_per_asset": total_hours / len(all_hour_usage)}

            # Calculate daily averages for hours
            daily_hours = {"daily_averages": [{"date": date_created.strftime("%Y-%m-%d"), "daily_average_per_asset": hours} for hours, date_created in all_hour_usage]}

            # Calculate weekly averages for hours
            weekly_hours = {"weekly_averages": []}
            current_week_start = None
            current_week_end = None
            weekly_data = []

            for hours, date_created in all_hour_usage:
                if current_week_start is None:
                    current_week_start = date_created.date()
                    current_week_end = current_week_start + datetime.timedelta(days=6)
                elif date_created.date() > current_week_end:
                    weekly_average = sum(weekly_data) / len(weekly_data)
                    weekly_hours["weekly_averages"].append({
                        "start_date": current_week_start.strftime("%Y-%m-%d"),
                        "end_date": current_week_end.strftime("%Y-%m-%d"),
                        "weekly_average_per_asset": weekly_average
                    })
                    current_week_start += datetime.timedelta(days=7)
                    current_week_end = current_week_start + datetime.timedelta(days=6)
                    weekly_data = []

                weekly_data.append(hours)

            if weekly_data:
                weekly_average = sum(weekly_data) / len(weekly_data)
                weekly_hours["weekly_averages"].append({
                    "start_date": current_week_start.strftime("%Y-%m-%d"),
                    "end_date": current_week_end.strftime("%Y-%m-%d"),
                    "weekly_average_per_asset": weekly_average
                })

            # Calculate monthly averages for hours
            monthly_hours = {"monthly_averages": []}
            current_month = None
            monthly_data = []

            for hours, date_created in all_hour_usage:
                if current_month is None:
                    current_month = date_created.date().replace(day=1)
                elif date_created.date().replace(day=1) != current_month:
                    monthly_average = sum(monthly_data) / len(monthly_data)
                    monthly_hours["monthly_averages"].append({
                        "month": current_month.strftime("%Y-%m"),
                        "monthly_average_per_asset": monthly_average
                    })
                    current_month += relativedelta(months=1)
                    monthly_data = []

                monthly_data.append(hours)

            if monthly_data:
                monthly_average = sum(monthly_data) / len(monthly_data)
                monthly_hours["monthly_averages"].append({
                    "month": current_month.strftime("%Y-%m"),
                    "monthly_average_per_asset": monthly_average
                })

        json_data = {"Mileage": {"yearly_average_per_asset": yearly_mileage, "daily_averages": daily_mileage, "weekly_averages": weekly_mileage, "monthly_averages": monthly_mileage}, "Hours": {"yearly_average_per_asset": yearly_hours, "daily_averages": daily_hours, "weekly_averages": weekly_hours, "monthly_averages": monthly_hours}}

        return json_data
    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_fleet_usage_percent(user, start_date, end_date):
        start_date = timezone.make_aware(timezone.datetime.strptime(start_date, "%Y-%m-%d"))
        end_date = timezone.make_aware(timezone.datetime.strptime(end_date, "%Y-%m-%d"))

        fleet_earliest_date = timezone.now()
        fleet_earliest_date = fleet_earliest_date.replace(year=fleet_earliest_date.year - 1)

        # In case it's a leap year
        fleet_earliest_date = fleet_earliest_date.replace(day=28 if (fleet_earliest_date.month == 2 and fleet_earliest_date.day == 29) else fleet_earliest_date.day)

        # Calculate fleet usage within the date range
        total_mileage = SnapshotDailyAsset.objects.using(user.db_access).exclude(hours_or_mileage="Hours").exclude(hours_or_mileage="Neither").filter(date_created__range=[start_date, end_date]).aggregate(total_mileage=Sum('daily_average_mileage'))['total_mileage']
        total_hours = SnapshotDailyAsset.objects.using(user.db_access).exclude(hours_or_mileage="Mileage").exclude(hours_or_mileage="Neither").filter(date_created__range=[start_date, end_date]).aggregate(total_hours=Sum('daily_average_hours'))['total_hours']

        # Calculate fleet usage percentage
        total_usage = total_mileage + total_hours
        fleet_usage_percent = (total_usage / (24 * 365)) * 100 if total_usage is not None else 0

        # Get total number of vehicles in the fleet
        total_vehicles = AssetModel.objects.using(user.db_access).count()

        return {
            "fleet_usage_percent": fleet_usage_percent,
            "total_vehicles": total_vehicles
        }


    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_fleet_usage(user):
        fleet_earliest_date = timezone.now()
        fleet_earliest_date = fleet_earliest_date.replace(year= fleet_earliest_date.year-1 )
        
        #incase its a leap year
        fleet_earliest_date = fleet_earliest_date.replace(day = 28 if (fleet_earliest_date.month==2 and fleet_earliest_date.day == 29) else fleet_earliest_date.day)
        #yearly average usage
        all_mileage_usage = SnapshotDailyAsset.objects.using(user.db_access).exclude(hours_or_mileage = "Hours").exclude(hours_or_mileage = "Neither").filter(date_created__range = [fleet_earliest_date,timezone.now()]).values_list('daily_average_mileage', 'date_created').order_by('date_created')
        all_hour_usage = SnapshotDailyAsset.objects.using(user.db_access).exclude(hours_or_mileage = "Mileage").exclude(hours_or_mileage = "Neither").filter(date_created__range = [fleet_earliest_date,timezone.now()]).values_list('daily_average_hours', 'date_created').order_by('date_created')
        
        yearly_mileage, yearly_hours = {"yearly_average_per_asset": 0.0}, {"yearly_average_per_asset": 0.0}
        daily_mileage, daily_hours = {"daily_averages": [{"date":"", "daily_average_per_asset": 0.0}]}, {"daily_averages": [{"date":"", "daily_average_per_asset": 0.0}]}
        if len(all_mileage_usage) > 0:
            yearly_mileage, daily_mileage = ChartCalculations.get_average_over_time(all_mileage_usage)
        if len(all_hour_usage) > 0:
            yearly_hours, daily_hours = ChartCalculations.get_average_over_time(all_hour_usage)
        
        json_data = {"Mileage":[yearly_mileage, daily_mileage], "Hours":[yearly_hours, daily_hours]}

        return json_data
    
    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_average_over_time(all_usage_histories):
        if all_usage_histories.count() > 0:
            all_known_usage_averages, all_dates = zip(*all_usage_histories)
            counter = 0
            days = 1
            year_total = 0
            daily_total = 0
            daily_totals = {}
            assets = 0
            total_assets = 0
            current_date = all_dates[0].date()

            daily_totals_json =[]
            
            for date in all_dates:
                year_total += all_known_usage_averages[counter]
                #calculate average per day
                if(date.date() != current_date):
                    daily_totals = {"date":current_date,"daily_average_per_asset":daily_total/assets}
                    total_assets += assets
                    assets = 0
                    daily_totals_json.append(daily_totals)
                    current_date= date.date()
                    daily_total = 0
                    days += 1
                daily_total += all_known_usage_averages[counter]  
                assets += 1
                counter += 1
            daily_totals = {"date":all_dates[counter-1].date(), "daily_average_per_asset":daily_total/assets}
            total_assets += assets
            daily_totals_json.append(daily_totals)
            yearly_total = {"yearly_average_per_asset":year_total/days/assets}
            daily_totals_json_named = {"daily_averages":daily_totals_json}
            return yearly_total,daily_totals_json_named

        else:
            return 0

    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_fuel_usage_dollar():
        
        '''data_actual = [ { "2016": 666724 }, { "2017": 618401 }, { "2018": 578303 }, { "2019": 581859 } ]
        data_projected = [ { "2016": 602048}, { "2017": 605345 }, { "2018": 600978 }, { "2019": 595944 } ]
        data = [{"actual":data_actual}, {"projected":data_projected}]
        '''

        '''data = [
            {"date": datetime(2016, 1, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 644513, "projected": 599345},
            {"date": datetime(2016, 2, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 651523, "projected": 600325},
            {"date": datetime(2016, 3, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 652428, "projected": 601325},
            {"date": datetime(2016, 4, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 654513, "projected": 601345},
            {"date": datetime(2016, 5, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 659387, "projected": 601139},
            {"date": datetime(2016, 6, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 666724, "projected": 602048},
            {"date": datetime(2016, 7, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 654511, "projected": 609345},
            {"date": datetime(2016, 8, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 652111, "projected": 608112},
            {"date": datetime(2016, 9, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 656377, "projected": 611134},
            {"date": datetime(2016, 10, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 656713, "projected": 612445},
            {"date": datetime(2016, 11, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 634518, "projected": 611541},
            {"date": datetime(2016, 12, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 620122, "projected": 610344},
            {"date": datetime(2017, 1, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 620013, "projected": 600349},
            {"date": datetime(2017, 2, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 618513, "projected": 609129},
            {"date": datetime(2017, 3, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 624515, "projected": 609925},
            {"date": datetime(2017, 4, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 639211, "projected": 611345},
            {"date": datetime(2017, 5, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 624518, "projected": 608811},
            {"date": datetime(2017, 6, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 618401, "projected": 605345},
            {"date": datetime(2017, 7, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 624513, "projected": 609111},
            {"date": datetime(2017, 8, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 614780, "projected": 609990},
            {"date": datetime(2017, 9, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 616717, "projected": 611541},
            {"date": datetime(2017, 10, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 615248, "projected": 610176},
            {"date": datetime(2017, 11, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 609743, "projected": 601646},
            {"date": datetime(2017, 12, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 619412, "projected": 602987},
            {"date": datetime(2018, 1, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 600013, "projected": 600123},
            {"date": datetime(2018, 2, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 591321, "projected": 600310},
            {"date": datetime(2018, 3, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 585935, "projected": 600761},
            {"date": datetime(2018, 4, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 580135, "projected": 600911},
            {"date": datetime(2018, 5, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 574024, "projected": 601023},
            {"date": datetime(2018, 6, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 578303, "projected": 600978},
            {"date": datetime(2018, 7, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 565134, "projected": 600513},
            {"date": datetime(2018, 8, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 570495, "projected": 600211},
            {"date": datetime(2018, 9, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 569013, "projected": 599121},
            {"date": datetime(2018, 10, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 580492, "projected": 599576},
            {"date": datetime(2018, 11, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 593049, "projected": 597631},
            {"date": datetime(2018, 12, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 583128, "projected": 596130},
            {"date": datetime(2019, 1, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 560302, "projected": 593724},
            {"date": datetime(2019, 2, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 572049, "projected": 592038},
            {"date": datetime(2019, 3, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 594828, "projected": 591203},
            {"date": datetime(2019, 4, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 600032, "projected": 591239},
            {"date": datetime(2019, 5, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 551029, "projected": 595694},
            {"date": datetime(2019, 6, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 581859, "projected": 595944},
            {"date": datetime(2019, 7, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 593829, "projected": 599982},
            {"date": datetime(2019, 8, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 593192, "projected": 600213},
            {"date": datetime(2019, 9, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 601293, "projected": 592034},
            {"date": datetime(2019, 10, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 583723, "projected": 587234},
            {"date": datetime(2019, 11, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 581928, "projected": 592131},
            {"date": datetime(2019, 12, 1).replace(tzinfo=timezone.utc).timestamp(), "actual": 579384, "projected": 591238}
        ]'''

        return None
        
    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_fuel_usage_volume():

        data_actual = [ { "year_1": 72 }, { "year_2": 78 }, { "year_3": 75 } ]
        data_projected = [ { "year_1": 45 }, { "year_2": 88 }, { "year_3": 67 } ]
        data = [{"actual":data_actual}, {"projected":data_projected}]

        return data

    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_asset_lifecycle_count(user):
      
        # TODO: stub data atm as requested. implement once FE starts work.
        return {"green":44,"yellow":33,"red":22}
      
        asset_qs =  AssetHelper.filter_assets_for_user(AssetHelper.get_all_assets(user.db_access), user)
        return ChartCalculations.get_asset_usage_lifecycle_count(asset_qs)

    @staticmethod
    def get_asset_lifecycle_count_by_type(user):
        asset_types = AssetTypeHelper.get_all_asset_types(user.db_access).values_list('name', flat=True)
        data = []
        all_asset_qs = AssetHelper.filter_assets_for_user(AssetHelper.get_all_assets(user.db_access), user)
        for asset_type in asset_types:
            asset_qs = all_asset_qs.filter(equipment_type__asset_type__name=asset_type)
            payload = ChartCalculations.get_asset_usage_lifecycle_count(asset_qs)
            container = {asset_type: payload}
            data.append(container)
        return data

    @staticmethod
    def get_asset_usage_lifecycle_count(asset_qs):
        green_count = 0
        yellow_count = 0
        red_count = 0

        for asset in asset_qs.iterator():
            green, yellow, red = 0, 0, 0
            hours_or_mileage = asset.hours_or_mileage.lower()
            if hours_or_mileage == AssetModel.Mileage.lower() or hours_or_mileage == AssetModel.Both.lower():
                if asset.replacement_mileage > 0:
                    current_mileage = asset.mileage
                    replacement_mileage = asset.replacement_mileage
                    projected_annual_mileage = asset.daily_average_mileage * 365
                    green, yellow, red = ChartCalculations.get_green_yellow_red(current_mileage, replacement_mileage, projected_annual_mileage)
            elif hours_or_mileage == AssetModel.Hours.lower():
                if asset.replacement_hours > 0:
                    current_hours = asset.hours
                    replacement_hours = asset.replacement_hours
                    projected_annual_hours = asset.daily_average_hours * 365
                    green, yellow, red = ChartCalculations.get_green_yellow_red(current_hours, replacement_hours, projected_annual_hours)
            else:
                break

            green_count += green
            yellow_count += yellow
            red_count += red

        return {"green": green_count, "yellow": yellow_count, "red": red_count}

    @staticmethod
    def get_green_yellow_red(current_usage, replacement_usage, projected_annual_usage):
        green_count = 0
        yellow_count = 0
        red_count = 0
        if(current_usage >= replacement_usage):
            red_count += 1
        elif(current_usage + projected_annual_usage < replacement_usage):
            green_count += 1
        else:
            yellow_count += 1

        return green_count, yellow_count, red_count

    #---------------------------------------------------------------------------------------------------

    '''
    Total spent on parts labour and fuel.
    Show op cost of each year.

    Green: 0 - 2.20
    Yellow: 2.21 - 3.90
    Red: 3.91 - 10

    total hours per year = 133452

                {"2019": [
                {"total:": 776522},
            ]},
            {"2018": [
                {"parts": 98732},
                {"labour": 97017},
                {"fuel": 578303}
            ]},
            {"2017": [
                {"parts": 128262},
                {"labour": 99340},
                {"fuel": 618401}
            ]},
            {"2016": [
                {"parts": 91307},
                {"labour": 40120},
                {"fuel": 666724}
            ]}

    '''

    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def get_operational_cost(user):

        db_name = user.db_access

        # get all relevant data from the database
        locations = list(LocationHelper.get_all_locations(db_name).values_list('location_id', 'location_name'))
        location_cost = list(SnapshotDailyLocationCost.objects.using(db_name).order_by('location', 'date_created'))
        location_asset_count = list(SnapshotDailyLocationCounts.objects.using(db_name).order_by('location', 'date_created'))

        # calculate the avg number of assets by location and month
        avg_assets_by_location = ChartCalculationsHelper.get_avg_assets_by_location_month(location_asset_count)
        # calculate the operational cost by location and month
        op_cost_by_loc = ChartCalculationsHelper.get_operational_cost_by_location(location_cost, avg_assets_by_location)

        result = list()
        for location in locations:
            location_id = location[0]
            location_name = location[1]
            result.append({location_name: op_cost_by_loc[location_id] if location_id in op_cost_by_loc else {}})

        return result

    #---------------------------------------------------------------------------------------------------

    @staticmethod
    def process_cost_by_location(user):
        db_name = user.db_access

        # get all locations
        locations = list(LocationHelper.get_all_locations(db_name))

        # get all repairs
        repairs = RepairHelper.get_all_repairs(db_name)
        repair_ids = [repair.repair_id for repair in repairs]

        # create dictionary of delivery costs by repair
        delivery_cost_by_repair = {dc.repair.repair_id : dc.total_cost for dc in DeliveryHelper.get_delivery_cost_by_repair_list(repairs, db_name)}

        # create dicitionary of rental cost by repair
        rental_cost_by_repair = {}
        for rent_cost in RentalHelper.get_rental_cost_by_repair_ids(repair_ids, db_name):
            repair_id = rent_cost.repair.repair_id
            rental_cost_by_repair[repair_id] = rental_cost_by_repair.get(repair_id, 0) + rent_cost.total_cost

        # get all maintenace records
        maintenance_records = MaintenanceHelper.get_all_maintenance(db_name)
        maintenance_ids = [maintenance.maintenance_id for maintenance in maintenance_records]

        # create dictionary of delivery cost by maintenance
        delivery_costs_by_maintenance = {dc.maintenance.maintenance_id : dc.total_cost for dc in DeliveryHelper.get_delivery_cost_by_maintenance_ids(maintenance_ids, db_name)}

        # create dictionary of labor cost by maintenance
        labor_costs_by_maintenance = {}
        for lab_cost in LaborHelper.get_labor_cost_by_maintenance_ids(maintenance_ids, db_name):
            maintenance_id = lab_cost.maintenance.maintenance_id
            labor_costs_by_maintenance[maintenance_id] = labor_costs_by_maintenance.get(maintenance_id, 0) + lab_cost.total_cost

        # create dictionary of parts cost by maintenance
        parts_costs_by_maintenance =  {}
        for part_cost in PartsHelper.get_parts_by_maintenance_ids(maintenance_ids, db_name):
            maintenance_id = part_cost.maintenance.maintenance_id
            parts_costs_by_maintenance[part_cost.maintenance.maintenance_id] = parts_costs_by_maintenance.get(maintenance_id, 0) + part_cost.total_cost

        # create dicitionary of rental cost by maintenance
        rental_cost_by_maintenance = {}
        for rent_cost in RentalHelper.get_rental_cost_by_maintenance_ids(maintenance_ids, db_name):
            maintenance_id = rent_cost.maintenance.maintenance_id
            rental_cost_by_maintenance[maintenance_id] = rental_cost_by_maintenance.get(maintenance_id, 0) + rent_cost.total_cost

        # get all accidents
        accidents = AccidentHelper.get_all_accidents(db_name)
        accident_ids = [accident.accident_id for accident in accidents]

        # create dictionary of insurance cost by accident
        insurance_cost_by_accident = {}
        for ins_cost in InsuranceHelper.get_insurance_cost_by_accident_ids(accident_ids, db_name):
            accident_id = ins_cost.accident.accident_id
            insurance_cost_by_accident[accident_id] = insurance_cost_by_accident.get(accident_id, 0) + ins_cost.total_cost

        # create dictionary of rental cost by accident
        rental_cost_by_accident = {}
        for rent_cost in RentalHelper.get_rental_cost_by_accident_ids(accident_ids, db_name):
            accident_id = rent_cost.accident.accident_id
            rental_cost_by_accident[accident_id] = rental_cost_by_accident.get(accident_id, 0) + rent_cost.total_cost

        # get all issues
        issues = IssueHelper.get_all_issues(db_name)
        issue_ids = [issue.issue_id for issue in issues]

        # create dictionary of labor cost by issue
        labor_costs_by_issue = {}
        for lab_cost in LaborHelper.get_labor_cost_by_issue_ids(issue_ids, db_name):
            issue_id = lab_cost.issue.issue_id
            labor_costs_by_issue[issue_id] = labor_costs_by_issue.get(issue_id, 0) + lab_cost.total_cost

        # create dictionary of parts cost by issue
        parts_costs_by_issue =  {}
        for part_cost in PartsHelper.get_parts_by_issue_list(issue_ids, db_name):
            issue_id = part_cost.issue.issue_id
            parts_costs_by_issue[issue_id] = parts_costs_by_issue.get(issue_id, 0) + part_cost.total_cost

        # create dictionaries of issue cost by repair and issue cost by accident
        issue_cost_by_repair, issue_cost_by_accident = {}, {}
        for issue in issues:
            issue_id = issue.issue_id
            issue_cost = labor_costs_by_issue.get(issue_id, 0) + parts_costs_by_issue.get(issue_id, 0)
            if issue.accident_id is not None:
                accident_id = issue.accident_id.accident_id
                issue_cost_by_accident[accident_id] = issue_cost_by_accident.get(accident_id, 0) + issue_cost
            if issue.repair_id is not None:
                repair_id = issue.repair_id.repair_id
                issue_cost_by_repair[repair_id] = issue_cost_by_repair.get(repair_id, 0) + issue_cost

        # create a dictionary of repairs by location
        repairs_by_location = {}
        for repair in repairs:
            if repair.location.location_id in repairs_by_location:
                repairs_by_location[repair.location.location_id].append(repair)
            else:
                repairs_by_location[repair.location.location_id] = [repair]

        # create a dictionary of maintenance records by location
        maintenance_by_location = {}
        for maintenance in maintenance_records:
            if maintenance.location.location_id in maintenance_by_location:
                maintenance_by_location[maintenance.location.location_id].append(maintenance)
            else:
                maintenance_by_location[maintenance.location.location_id] = [maintenance]

        # create a dictionary of accidents by location
        accidents_by_location = {}
        for accident in accidents:
            if accident.location.location_id in accidents_by_location:
                accidents_by_location[accident.location.location_id].append(accident)
            else:
                accidents_by_location[accident.location.location_id] = [accident]


        nested_dict = lambda: defaultdict(nested_dict)
        result = nested_dict()

        # loop through each location
        for location in locations:
            location_name = location.location_name
            location_id = location.location_id
            repair_process = 'repair'
            maintenance_process = 'maintenance'
            accident_process = 'accident'

            # append the repair cost for each repair in the current locaion
            for repair in repairs_by_location.get(location_id, []):
                year = repair.date_created.year
                month = calendar.month_name[repair.date_created.month]
                repair_id = repair.repair_id
                old_value = ChartCalculationsHelper.get_existing_value_or_zero(result, location_name, year, month, repair_process)

                result[location_name][year][month][repair_process] = old_value \
                                                            + issue_cost_by_repair.get(repair_id, 0) \
                                                            + delivery_cost_by_repair.get(repair_id, 0) \
                                                            + rental_cost_by_repair.get(repair_id, 0)
                result[location_name][year][month][maintenance_process] = result[location_name][year][month].get(maintenance_process, 0)
                result[location_name][year][month][accident_process] = result[location_name][year][month].get(accident_process, 0)

            # append the maintenance cost for each maintenance in the current locaion
            for maintenance in maintenance_by_location.get(location_id, []):
                year = maintenance.date_created.year
                month = calendar.month_name[maintenance.date_created.month]
                maintenance_id = maintenance.maintenance_id
                old_value = ChartCalculationsHelper.get_existing_value_or_zero(result, location_name, year, month, maintenance_process)
                result[location_name][year][month][maintenance_process] = old_value \
                                                            + parts_costs_by_maintenance.get(maintenance_id, 0) \
                                                            + labor_costs_by_maintenance.get(maintenance_id, 0) \
                                                            + delivery_costs_by_maintenance.get(maintenance_id, 0) \
                                                            + rental_cost_by_maintenance.get(maintenance_id, 0)
                result[location_name][year][month][repair_process] = result[location_name][year][month].get(repair_process, 0)
                result[location_name][year][month][accident_process] = result[location_name][year][month].get(accident_process, 0)

            # append the accident cost for each accident in the current locaion
            for accident in accidents_by_location.get(location_id, []):
                year = accident.date_created.year
                month = calendar.month_name[accident.date_created.month]
                accident_id = accident.accident_id
                old_value = ChartCalculationsHelper.get_existing_value_or_zero(result, location_name, year, month, accident_process)

                result[location_name][year][month][accident_process] = old_value \
                                                            + issue_cost_by_accident.get(accident_id, 0) \
                                                            + insurance_cost_by_accident.get(accident_id, 0) \
                                                            + rental_cost_by_accident.get(accident_id, 0)
                result[location_name][year][month][repair_process] = result[location_name][year][month].get(repair_process, 0)
                result[location_name][year][month][maintenance_process] = result[location_name][year][month].get(maintenance_process, 0)

        return result
    
    @staticmethod
    def work_order_completion_time(user):
        try:
            db_name = user.db_access
            today = date.today()

            repairs_avg_completion_time = RepairsModel.objects.using(db_name).exclude(date_completed=None).annotate(duration=ExpressionWrapper(F('date_created') - today, output_field=DurationField())).aggregate(avg_completion_time=Avg('duration'))

            maintenance_avg_completion_time = MaintenanceRequestModel.objects.using(db_name).exclude(date_completed=None).annotate(duration=ExpressionWrapper(F('date_created') - today, output_field=DurationField())).aggregate(avg_completion_time=Avg('duration'))

            avg_completion_time_days = (repairs_avg_completion_time['avg_completion_time'] + maintenance_avg_completion_time['avg_completion_time']) / 2

            # Convert timedelta to days for serialization
            repairs_avg_completion_time_days = repairs_avg_completion_time['avg_completion_time'].total_seconds() / 86400
            maintenance_avg_completion_time_days = maintenance_avg_completion_time['avg_completion_time'].total_seconds() / 86400
            total_avg_completion_time_days = avg_completion_time_days.total_seconds() / 86400

            response_data = {
                'repairs_avg_completion_days': repairs_avg_completion_time_days,
                'maintenance_avg_completion_days': maintenance_avg_completion_time_days,
                'total_avg_completion_days': total_avg_completion_time_days
            }

            return response_data
        except Exception as e:
            traceback.print_exc()
            logging.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            error_response = CustomError.get_full_error_json(CustomError.G_0, e)
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)
