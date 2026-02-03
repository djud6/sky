from rest_framework.response import Response
from rest_framework import status
from api.Models.RolePermissions import RolePermissions
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RolePermissionsUpdater():

    @staticmethod
    def create_role_permissions_entry(role_permissions_data):
        return RolePermissions(
            role = role_permissions_data.get("role").strip(),
            fleet_at_a_glance = role_permissions_data.get("fleet_at_a_glance").strip(),
            fleet_at_a_glance_executive = role_permissions_data.get("fleet_at_a_glance_executive").strip(),
            fleet_at_a_glance_manager = role_permissions_data.get("fleet_at_a_glance_manager").strip(),
            fleet_overview = role_permissions_data.get("fleet_overview").strip(),
            asset_request = role_permissions_data.get("asset_request").strip(),
            asset_request_new_order = role_permissions_data.get("asset_request_new_order").strip(),
            asset_request_list = role_permissions_data.get("asset_request_list").strip(),
            repairs = role_permissions_data.get("repairs").strip(),
            repairs_list = role_permissions_data.get("repairs_list"),
            repairs_new_request = role_permissions_data.get("repairs_new_request").strip(),
            maintenance = role_permissions_data.get("maintenance").strip(),
            maintenance_status = role_permissions_data.get("maintenance_status").strip(),
            maintenance_new_request = role_permissions_data.get("maintenance_new_request").strip(),
            maintenance_forecast = role_permissions_data.get("maintenance_forecast").strip(),
            maintenance_lookup = role_permissions_data.get("maintenance_lookup").strip(),
            incidents = role_permissions_data.get("incidents").strip(),
            incidents_list = role_permissions_data.get("incidents_list").strip(),
            incidents_new_report = role_permissions_data.get("incidents_new_report").strip(),
            issues = role_permissions_data.get("issues").strip(),
            issues_new = role_permissions_data.get("issues_new").strip(),
            issues_list = role_permissions_data.get("issues_list").strip(),
            issues_search = role_permissions_data.get("issues_search").strip(),
            operators = role_permissions_data.get("operators").strip(),
            operators_daily_check = role_permissions_data.get("operators_daily_check").strip(),
            operators_search = role_permissions_data.get("operators_search").strip(),
            unfinished_checks = role_permissions_data.get("unfinished_checks").strip(),
            energy = role_permissions_data.get("energy").strip(),
            energy_fuel_tracking = role_permissions_data.get("energy_fuel_tracking").strip(),\
            fuel_transactions = role_permissions_data.get("fuel_transactions").strip(),
            asset_removal = role_permissions_data.get("asset_removal").strip(),
            asset_removal_new = role_permissions_data.get("asset_removal_new").strip(),
            asset_removal_list = role_permissions_data.get("asset_removal_list").strip(),
            approval_request = role_permissions_data.get("approval_request").strip(),
            asset_transfers = role_permissions_data.get("asset_transfers").strip(),
            asset_transfers_current_transfers = role_permissions_data.get("asset_transfers_current_transfers").strip(),
            asset_transfers_new_transfer_request = role_permissions_data.get("asset_transfers_new_transfer_request").strip(),
            asset_transfers_map = role_permissions_data.get("asset_transfers_map").strip(),
            asset_log = role_permissions_data.get("asset_log").strip()
        )