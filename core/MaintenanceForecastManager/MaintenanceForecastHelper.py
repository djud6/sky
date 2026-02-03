import logging
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response

from GSE_Backend.errors.ErrorDictionary import CustomError
from api.Models.asset_model import AssetModel
from api.Models.maintenance_forecast import MaintenanceForecastRules
from api.Models.maintenance_forecast_history import MaintenanceForecastRulesHistory
from api.Models.maintenance_request import MaintenanceRequestModel
from ..AssetManager.AssetHelper import AssetHelper
from ..Helper import HelperMethods


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceForecastHelper:

    @staticmethod
    def get_maintenance_forecast_rules(db_name):
        return MaintenanceForecastRules.objects.using(db_name).all()

    @staticmethod
    def get_maintenance_forecast_rules_by_vin(_vin, db_name):
        return MaintenanceForecastRules.objects.using(db_name).filter(VIN=_vin)

    @staticmethod
    def get_maintenance_forecast_rule_by_vin_and_type(_vin, _type, relevant_engine, db_name):
        return MaintenanceForecastRules.objects.using(db_name).get(VIN=_vin, inspection_type=_type,
                                                                   linked_engine=relevant_engine)

    @staticmethod
    def get_maintenance_forecast_rules_for_daterange(start_date, end_date, db_name):
        return MaintenanceForecastRules.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_maintenance_forecast_rule_history_for_daterange(start_date, end_date, db_name):
        return MaintenanceForecastRulesHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_maintenance_forecast_rule_by_id(maintenance_rule_id, db_name):
        try:
            return MaintenanceForecastRules.objects.using(db_name).get(id=maintenance_rule_id), Response(
                status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MRDNE_2, e))
            return None, Response(CustomError.get_full_error_json(CustomError.MRDNE_2, e),
                                  status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_maintenance_forecast_rule_by_custom_id(custom_maintenance_rule_id, db_name):
        try:
            return MaintenanceForecastRules.objects.using(db_name).get(custom_id=custom_maintenance_rule_id), Response(
                status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MRDNE_3, e))
            return None, Response(CustomError.get_full_error_json(CustomError.MRDNE_3, e),
                                  status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    # Checks to make sure the rule being requested to add doesn't already exist for the inspection type and vin
    def validate_entry(proposed):
        try:
            matches = MaintenanceForecastRules.objects.filter(
                VIN=proposed.validated_data.get("VIN"),
                inspection_type=proposed.validated_data.get("inspection_type"),
                linked_engine=proposed.validated_data.get("linked_engine")
            )

            return len(matches) == 0

        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def forecast_maintenance(db_name, inspection_type_obj, start_date, end_date):
        try:
            # Ignore Disposed-of assets.
            all_relevant_vins = AssetHelper.get_all_assets(db_name).values_list("VIN", flat=True)

            # All rules in db that match the specified inspection types and that are not linked to any engine.
            rules_qs = inspection_type_obj.maintenanceforecastrules_set.filter(VIN__in=all_relevant_vins,
                                                                               linked_engine=None).values()

            # All Assets that have a rule of the specified inspection types.
            all_relevant_vins = rules_qs.values_list("VIN", flat=True)
            assets_qs = AssetHelper.get_assets_from_VIN_list(all_relevant_vins, db_name).values()

            # All complete maintenance requests for the VINs in vins_list that match an inspection type.
            complete_statuses = [MaintenanceRequestModel.complete, MaintenanceRequestModel.delivered]
            maintenance_qs = inspection_type_obj.maintenancerequestmodel_set.filter(VIN__in=all_relevant_vins,
                                                                                    status__in=complete_statuses).values()
            vins_with_maintenance_requests = maintenance_qs.values_list("VIN", flat=True)

            # Assets that have a rule for this inspection type and that we can forecast.
            assets_VIN_list = []

            # The forecast maintenance for each asset in assets_VIN_list
            assets_maintenance_date = {}

            # Assets that we don't have previous maintenance data for,
            # so we can not forecast, but that have a rule for this inspection type.
            assets_potential_maintenance_VIN_list = []

            # Go through every rule.
            for rule_obj in rules_qs:
                asset_vin = rule_obj.get('VIN_id')

                # If the asset have previously completed maintenances of this type of inspection
                # then check if it's due for another inspection in the specified timespan.
                # Else, if the asset has no history of this type of inspection then don't forecast for it and
                # add it as a potential maintenance.
                if asset_vin in vins_with_maintenance_requests:
                    asset_dict = assets_qs.get(VIN=asset_vin)
                    latest_maintenance_report = maintenance_qs.filter(VIN=asset_vin).latest('date_completed')
                    next_maintenance_date = MaintenanceForecastHelper.inspection_due(asset_dict,
                                                                                     latest_maintenance_report,
                                                                                     rule_obj,
                                                                                     start_date,
                                                                                     end_date)

                    if next_maintenance_date:
                        assets_VIN_list.append(asset_vin)
                        assets_maintenance_date[asset_vin] = next_maintenance_date

                else:
                    assets_potential_maintenance_VIN_list.append(asset_vin)

            return assets_VIN_list, assets_maintenance_date, assets_potential_maintenance_VIN_list, Response(
                status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, None, Response(CustomError.get_full_error_json(CustomError.G_0, e),
                                        status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def inspection_due(asset_dict, latest_maintenance_report_obj, rule_obj, start_date, end_date):

        hours_or_mileage = asset_dict.get('hours_or_mileage')
        current_mileage = asset_dict.get('mileage')
        current_hours = asset_dict.get('hours')
        daily_average_mileage = asset_dict.get('daily_average_mileage')
        daily_average_hours = asset_dict.get('daily_average_hours')

        latest_maintenance_date = latest_maintenance_report_obj.get('date_completed')
        latest_maintenance_mileage = latest_maintenance_report_obj.get('mileage')
        latest_maintenance_hours = latest_maintenance_report_obj.get('hours')

        cycle_mileage = rule_obj.get('mileage_cycle')
        cycle_hours = rule_obj.get('hour_cycle')
        cycle_time = rule_obj.get('time_cycle')

        current_date = datetime.utcnow()

        maintenance_required_date = datetime.max

        next_maintenance_date_found = False

        if cycle_hours > 0 and (hours_or_mileage == AssetModel.Hours or hours_or_mileage == AssetModel.Both):
            next_maintenance_date = MaintenanceForecastHelper.due_date_in_range_by_usage(start_date, end_date,
                                                                                         latest_maintenance_hours,
                                                                                         cycle_hours, current_hours,
                                                                                         daily_average_hours,
                                                                                         current_date)
            if next_maintenance_date is not None:
                if next_maintenance_date < maintenance_required_date:
                    maintenance_required_date = next_maintenance_date
                    next_maintenance_date_found = True

        if cycle_mileage > 0 and (hours_or_mileage == AssetModel.Mileage or hours_or_mileage == AssetModel.Both):
            next_maintenance_date = MaintenanceForecastHelper.due_date_in_range_by_usage(start_date, end_date,
                                                                                         latest_maintenance_mileage,
                                                                                         cycle_mileage, current_mileage,
                                                                                         daily_average_mileage,
                                                                                         current_date)
            if next_maintenance_date is not None:
                if next_maintenance_date < maintenance_required_date:
                    maintenance_required_date = next_maintenance_date
                    next_maintenance_date_found = True

        if cycle_time > 0:
            next_maintenance_date = MaintenanceForecastHelper.due_date_in_range_by_usage(start_date, end_date,
                                                                                         latest_maintenance_date,
                                                                                         cycle_time, cycle_time=True)
            if next_maintenance_date is not None:
                if next_maintenance_date < maintenance_required_date:
                    maintenance_required_date = next_maintenance_date
                    next_maintenance_date_found = True

        if next_maintenance_date_found:
            return maintenance_required_date
        return None

    @staticmethod
    def due_date_in_range_by_usage(start_date, end_date, latest_maintenance_units, cycle_units,
                                   current_units=None, daily_average_units=None,
                                   current_date=None, cycle_time=False):
        try:
            if cycle_time is False:
                units_since_last_maintenance = current_units - latest_maintenance_units
                units_until_next_maintenance = cycle_units - units_since_last_maintenance
                days_till_maintenance = units_until_next_maintenance / daily_average_units
                maintenance_required_date = HelperMethods.add_time_to_datetime(current_date, days_till_maintenance,
                                                                               time_unit="days").replace(tzinfo=None)
            else:
                maintenance_required_date = HelperMethods.add_time_to_datetime(latest_maintenance_units, cycle_units,
                                                                               time_unit="days").replace(tzinfo=None)

            if start_date <= maintenance_required_date <= end_date:
                # DUE DATE IN RANGE
                return maintenance_required_date
            elif start_date > maintenance_required_date < datetime.utcnow():
                # DUE DATE IS OVERDUE
                return maintenance_required_date
            else:
                # DUE DATE NOT IN RANGE
                return None

        except ZeroDivisionError as zde:
            extra_info = f"Average daily usage for this asset is 0 --> Skipping forecast. {zde}"
            Logger.getLogger().error(extra_info)
            return None
        except Exception as e:
            Logger.getLogger().error(e)
            return None

    @staticmethod
    def add_forecast_date_to_maintenance_ser(ser_data, forecast_date_dict):
        """
        Adds a maintenance forecast date to an AssetModel serialized list based on
        a dictionary of VIN/maintenance_date key/value pairs.
        """
        for asset_json in ser_data:
            try:
                asset_json['maintenance_due_date'] = forecast_date_dict[asset_json['VIN']]
            except KeyError:
                asset_json['maintenance_due_date'] = "NA"
        return ser_data
