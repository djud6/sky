from api.Models.Cost.license_cost_history import LicenseCostModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class LicenseCostHistory:

    @staticmethod
    def create_license_cost_record_by_obj(license_cost):
        try:
            license_cost_history_entry = LicenseCostHistory.generate_license_cost_history_entry(license_cost)
            license_cost_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_license_cost_history_entry(license_cost):
        return LicenseCostModelHistory(
            license_cost = license_cost,
            VIN = license_cost.VIN,
            license_registration = license_cost.license_registration,
            taxes = license_cost.taxes,
            license_plate_renewal = license_cost.license_plate_renewal,
            currency = license_cost.currency,
            total_cost = license_cost.total_cost,
            modified_by = license_cost.modified_by,
            location=license_cost.location
        )