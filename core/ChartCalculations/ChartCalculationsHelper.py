from api.Models.Cost.currency import Currency
from rest_framework import status
from api.Models.asset_model import AssetModel
from datetime import datetime, timedelta
from django.db.models.aggregates import Sum
from api.Serializers.serializers import IssueSerializer
from ..LocationManager.LocationHelper import LocationHelper
from api.Models.Snapshot.snapshot_daily_asset import SnapshotDailyAsset
from api.Models.asset_daily_checks import AssetDailyChecksModel
from datetime import date, datetime, timedelta
import calendar
from django.db.models.functions import TruncWeek, TruncMonth
import pytz
import operator



class ChartCalculationsHelper():

    # Expects a list of tuples that equal to int_field at their field_index 
    @staticmethod
    def get_subset_for_int_field(int_field, tuple_list, field_index=0):
        subset = []
        for tpl in tuple_list:
            if int(tpl[field_index]) == int(int_field):
                subset.append(tpl)
        return subset

    # Expects a list of tuples that equal to str_field at their field_index 
    @staticmethod
    def get_subset_for_str_field(str_field, tuple_list, field_index=0):
        subset = []
        for tpl in tuple_list:
            if str(tpl[field_index]) == str(str_field):
                subset.append(tpl)
        return subset

    # Expects a list of tuples that have a location ID elem that equals int_field
    @staticmethod
    def get_subset_for_location_field(int_field, tuple_list):
        
        return tuple_list.filter(location=int_field)


    
    # Expects a list of tuples that equal to date_field at their field_index 
    @staticmethod
    def get_subset_for_date_field(date_field, tuple_list, field_index=0):
        subset = []
        for tpl in tuple_list:
            tpl_date = tpl[field_index]
            if type(tpl_date) != type(date_field):
                tpl_date = tpl_date.date()
            if tpl_date == date_field:
                subset.append(tpl)
        return subset


    # Expects: 
    # - table_dict_list: The result of serializer.data (list of ordered dictionaries).
    # - field_list: a list of values (should match some column in table_dict_list).
    # - field_string: will identify which column field_list elems match with in table_dict_list.
    @staticmethod
    def get_dict_subset_in_field_list(field_string, field_list, table_dict_list):
        subset = []
        if len(field_list) < 1:
            return subset
        for entry in table_dict_list:
            if entry.get(field_string) in field_list:
                subset.append(entry)
        return subset


    # Expects: 
    # - table_tpl_list: The result of queryset.values_list().
    # - field_list: a list of values (should match some column in table_dict_list).
    # - field_index: will identify which field in tuple we are filtering by.
    @staticmethod
    def get_tpl_subset_in_field_list(field_list, table_tpl_list, field_index=0):
        subset = []
        if len(field_list) < 1:
            return subset
        for entry in table_tpl_list:
            if entry[field_index] in field_list:
                subset.append(entry)
        return subset


    # Expects list of tuples each being a process that include the process status (complete/incomplete)
    @staticmethod
    def get_complete_and_incomplete_counts_for_process(compare_to, process_list, status_index=0):
        complete_count = 0
        incomplete_count = 0
        for process in process_list:
            if process[status_index] == compare_to:
                complete_count += 1
            else:
                incomplete_count += 1
        return complete_count, incomplete_count

    @staticmethod
    def calculate_location_fuel_cost(location_cost_obj, interval):
        """
        Get the fuel cost per day/week/month and calculate the percentage of change from one day/week/month to another.
        :param location_cost_obj: List of dict containing the total fuel information per day for a specific location.
        :param interval: Interval to calculate the fuel cost. It can either be 'daily', 'weekly' or 'monthly'.
        """
        # General Initialization
        chart_data = []
        prev_total_cost = 0.0
        start_date, end_date = None, None
        current_year = None

        # Initialization for daily chart
        prev_fuel_cost = 0

        # Initialization for weekly chart
        total_weekly_cost = 0.0
        current_week = None
        is_first_day_of_current_week = True
        amount_of_weeks = 1

        # Initialization for monthly chart
        total_monthly_cost = 0.0
        current_month = None, None
        amount_of_months = 1
        is_first_day_of_month = True

        for index, location_snap in enumerate(location_cost_obj):
            if interval == 'daily':
                """
                Get the total fuel cost per day and calculate the percentage of change from one day to another.
                """
                if prev_fuel_cost == 0:
                    perc_change = 0
                else:
                    perc_change = (location_snap['total_cost_fuel'] / prev_fuel_cost) - 1
                    perc_change = round(perc_change, 2)

                chart_data.append({"date": location_snap['date_created'],
                                   "fuel_cost": location_snap['total_cost_fuel'],
                                   "currency": location_snap['currency'],
                                   "percentage_change": perc_change})

                prev_fuel_cost = location_snap['total_cost_fuel']

            elif interval == 'weekly':
                """
                Calculate the total fuel cost per week and the percentage of change from one week to another.
                """
                date_created = location_snap['date_created']
                is_last_item = index == len(location_cost_obj) - 1

                if index == 0:
                    start_date = date_created  # is this needed here?
                    end_date = date_created  # is this needed here?
                    current_week = date_created.strftime("%W")
                    current_year = date_created.year

                if date_created.strftime("%W") != current_week or date_created.year != current_year or is_last_item:
                    # this means that the previous week has finished, or it is the last entry in the for loop.
                    if is_last_item:
                        total_weekly_cost += location_snap['total_cost_fuel']
                        end_date = date_created

                    if prev_total_cost == 0:
                        perc_change = 0.0
                    else:
                        perc_change = round((total_weekly_cost / prev_total_cost) - 1, 2)

                    chart_data.append({"week": amount_of_weeks,
                                       "start_date": start_date,
                                       "end_date": end_date,
                                       "fuel_cost": total_weekly_cost,
                                       "currency": location_snap['currency'],
                                       "percentage_change": perc_change})
                    prev_total_cost = total_weekly_cost
                    total_weekly_cost = 0.0
                    current_week = date_created.strftime("%W")
                    current_year = date_created.year
                    start_date = None
                    end_date = None
                    is_first_day_of_current_week = True
                    amount_of_weeks += 1

                if date_created.year == current_year and is_last_item is False:
                    if date_created.strftime("%W") == current_week:
                        if is_first_day_of_current_week:
                            total_weekly_cost = location_snap['total_cost_fuel']
                            start_date = date_created
                            end_date = date_created
                            is_first_day_of_current_week = False
                        else:
                            total_weekly_cost += location_snap['total_cost_fuel']
                            end_date = date_created

            else:
                """
                Calculate the total fuel cost per month and the percentage of change from one month to another.
                """
                date_created = location_snap['date_created']
                is_last_item = index == len(location_cost_obj) - 1

                if index == 0:
                    start_date = date_created
                    end_date = date_created
                    current_month = date_created.month
                    current_year = date_created.year

                if date_created.month != current_month or date_created.year != current_year or is_last_item:
                    # this means that the previous month has finished, or it is the last entry in the for loop.
                    if is_last_item:
                        total_monthly_cost += location_snap['total_cost_fuel']
                        end_date = date_created

                    if prev_total_cost == 0:
                        perc_change = 0.0
                    else:
                        perc_change = round((total_monthly_cost / prev_total_cost) - 1, 2)

                    chart_data.append({"month": amount_of_months,
                                       "start_date": start_date,
                                       "end_date": end_date,
                                       "fuel_cost": total_monthly_cost,
                                       "currency": location_snap['currency'],
                                       "percentage_change": perc_change})
                    prev_total_cost = total_monthly_cost
                    total_monthly_cost = 0.0
                    current_month = date_created.month
                    current_year = date_created.year
                    start_date = None
                    end_date = None
                    is_first_day_of_month = True
                    amount_of_months += 1

                if date_created.year == current_year and is_last_item is False:
                    if date_created.month == current_month:
                        if is_first_day_of_month:
                            total_monthly_cost = location_snap['total_cost_fuel']
                            start_date = date_created
                            end_date = date_created
                            is_first_day_of_month = False
                        else:
                            total_monthly_cost += location_snap['total_cost_fuel']
                            end_date = date_created

        return chart_data

    @staticmethod
    def get_daily_checks_and_assets(user):
        db_name = user
        locations = list(LocationHelper.get_all_locations(db_name).values_list('location_id', 'location_name'))
        all_assets = list(SnapshotDailyAsset.objects.using(db_name).exclude(status=AssetModel.Disposed).values_list('current_location','date_created','status').order_by('date_created'))
        all_daily_checks = list(AssetDailyChecksModel.objects.using(db_name).exclude(location=None).values_list('daily_check_id','date_created', 'location'))
        daily_checks_and_assets = []
        for location_tuple in locations:
            location_id = location_tuple[0]
            start_date = datetime.utcnow().date() - timedelta(days=1)
            asset_location_filtered = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_assets, 0)
            all_assets_yesterday = ChartCalculationsHelper.get_subset_for_date_field(start_date, asset_location_filtered, 1)
            all_asset_count = len(all_assets_yesterday)
            active_asset_count = len(ChartCalculationsHelper.get_subset_for_str_field("Active", all_assets_yesterday, 2))
            daily_check_location_filtered = ChartCalculationsHelper.get_subset_for_int_field(location_id, all_daily_checks, 2)
            daily_check_count = len(ChartCalculationsHelper.get_subset_for_date_field(start_date, daily_check_location_filtered, 1))
            check = {}
            check['date_of_checks'] = start_date
            check['active_asset_count'] = active_asset_count
            check['daily_check_count'] = daily_check_count
            check['all_asset_count'] = all_asset_count
            check['location'] = location_id
            #These lines will return a json instead of a dictionary if desired
            #json_check = json.dumps(check,  sort_keys=True,indent=1,default=str)
            #date_and_volume.append(json_check)  
            daily_checks_and_assets.append(check)

        return daily_checks_and_assets

    @staticmethod
    def combine_similar(tuple_list):
        unique = []
        if len(tuple_list) > 0:
            previous = list(tuple_list[0])
            no_previous = True
            for i, val in enumerate(tuple_list):
                if(no_previous == True):
                    previous = list(val)
                    no_previous = False
                elif(val[0] == tuple_list[i-1][0] and val[1].date() == tuple_list[i-1][1].date() and val[4] == tuple_list[i-1][4]):
                    if(val[3] == 'liter'):
                        previous[2] = previous[2] + val[2]
                    elif(val[3] == 'gallon'):
                        previous[2] = previous[2] + val[2]*3.78541
                else:
                    unique.append(previous)
                    previous = list(val)
            if(len(tuple_list)>0):
                unique.append(previous)

        return unique

    # Expects a list of SnapshotDailyLocationCounts ordered in ascending order by location and date_created
    @staticmethod
    def get_avg_assets_by_location_month(daily_location_counts):
        result = dict()
        no_of_assets = 0
        count = 0
        for i, loc in enumerate(daily_location_counts):
            no_of_assets += loc.all_asset_count
            count += 1
            cur_month = loc.date_created.month
            cur_year = loc.date_created.year

            is_last_record = i == len(daily_location_counts) - 1
            # check if the next record is for a different month than the current record
            is_next_record_next_month = is_last_record or cur_month != daily_location_counts[i + 1].date_created.month or \
                cur_year != daily_location_counts[i + 1].date_created.year
            # check if the next record is for a different location than the current record
            is_next_records_location_different = is_last_record or loc.location != daily_location_counts[i + 1].location

            if is_next_record_next_month or is_next_records_location_different:
                # calculate average number of assets
                avg_no_assets = no_of_assets / count

                # store the average in a dictionary which can be accessed like so: result[location_id][month_name]
                if loc.location in result:
                    result[loc.location][calendar.month_name[cur_month]] = avg_no_assets
                else:
                    result[loc.location] = {calendar.month_name[cur_month]: avg_no_assets}
                no_of_assets = 0
                count = 0
        
        return result

    # Expects a list of SnapshotDailyLocationCost ordered in ascending order by location and date_created
    # Also expects a dictionary of the average number of assets per location per month (result of get_avg_assets_by_location_month)
    @staticmethod
    def get_operational_cost_by_location(locations, assets_by_loc_month):
        op_cost_by_loc = dict()
        running_sum = 0
        prev_cost_per_asset = 0

        for i, loc in enumerate(locations):
            cur_month = loc.date_created.month
            cur_year = loc.date_created.year
            loc_id = int(loc.location)
            cur_month_name = calendar.month_name[cur_month]

            # calculate the total cost of operating an asset
            running_sum += loc.total_cost_fuel + loc.total_cost_insurance + loc.total_cost_labor + \
                loc.total_cost_license + loc.total_cost_parts + loc.total_cost_rental

            is_last_record = i == len(locations) - 1
            # check if the next record is for a different month than the current record
            is_next_record_next_month = is_last_record or \
                cur_month != locations[i + 1].date_created.month or cur_year != locations[i + 1].date_created.year

            # check if the next record is for a different location than the current record
            is_next_records_location_different = is_last_record or loc.location != locations[i + 1].location

            if is_next_record_next_month or is_next_records_location_different:

                # check to see if the record for the average number of assets for the current location and month exists
                avg_assets_not_exists = loc_id not in assets_by_loc_month or \
                    cur_month_name not in assets_by_loc_month[loc_id] or \
                    not assets_by_loc_month[loc_id][cur_month_name]

                # if the average number of assets does not exist for the current location and month, then continue
                if avg_assets_not_exists:
                    running_sum = 0
                    continue

                # calculate the cost per asset as the sum divided by the average number of assets for the current location and month
                cost_per_asset = running_sum / assets_by_loc_month[loc_id][cur_month_name]

                # calculate the percentage change from previous month, 0 if previous month's record does not exist
                per_change = round(((cost_per_asset - prev_cost_per_asset) / prev_cost_per_asset)*100, 1) if prev_cost_per_asset else 0
                summary_obj = {
                    "month": cur_month_name, 
                    "year": cur_year,
                    "cost_per_asset": cost_per_asset,
                    "percentage_change": per_change
                }

                if loc_id in op_cost_by_loc:
                    op_cost_by_loc[loc_id].append(summary_obj)
                else:
                    op_cost_by_loc[int(loc.location)] = [summary_obj]

                # set prev_cost_per_asset to 0 when location changes
                if is_next_records_location_different:
                    prev_cost_per_asset = 0
                else:
                    prev_cost_per_asset = cost_per_asset
                running_sum = 0

        return op_cost_by_loc

    # To be used only for the process cost by location, month and process KPI
    @staticmethod
    def get_existing_value_or_zero(interim_result, location_name, year, month, process):
        return interim_result[location_name][year][month][process] if location_name in interim_result \
                    and year in interim_result[location_name] \
                    and month in interim_result[location_name][year] \
                    and process in interim_result[location_name][year][month] \
                    else 0
