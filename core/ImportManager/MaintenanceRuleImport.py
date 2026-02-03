from rest_framework.response import Response
from rest_framework import status
from ..MaintenanceManager.MaintenanceUpdater import MaintenanceUpdater
from ..MaintenanceForecastManager.MaintenanceForecastUpdater import MaintenanceForecastUpdater
from ..UserManager.UserHelper import UserHelper
from api.Models.maintenance_forecast import MaintenanceForecastRules
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceRuleImport():

    @staticmethod
    def import_maintenance_rule_csv(parsed_data, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            maintenance_rule_entries = []
            for maintenance_rule_row in parsed_data:
                if not MaintenanceForecastRules.objects.using(user.db_access).filter(VIN=maintenance_rule_row.get("VIN"), inspection_type__inspection_code=maintenance_rule_row.get("inspection_code")).exists():
                    if MaintenanceRuleImport.validate_rule_row(maintenance_rule_row, maintenance_rule_entries):
                        entry = MaintenanceForecastUpdater.create_maintenance_rule_entry(maintenance_rule_row, detailed_user, user.db_access)
                        maintenance_rule_entries.append(entry)
            MaintenanceForecastRules.objects.using(user.db_access).bulk_create(maintenance_rule_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_15, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_15, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def validate_rule_row(row, previous_entries):
        # Check to see if we've already had a rule of this type for this asset from the import csv
        for previous_entry in previous_entries:
            if row.get("VIN").lower() == previous_entry.VIN.VIN.lower() and row.get("inspection_code").lower() == previous_entry.inspection_type.inspection_code.lower():
                return False
        return True