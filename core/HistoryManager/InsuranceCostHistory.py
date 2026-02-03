from api.Models.Cost.insurance_cost_history import InsuranceCostModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class InsuranceCostHistory:

    @staticmethod
    def create_insurance_cost_record_by_obj(insurance_cost):
        try:
            insurance_cost_history_entry = InsuranceCostHistory.generate_insurance_cost_history_entry(insurance_cost)
            insurance_cost_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_insurance_cost_history_entry(insurance_cost):
        return InsuranceCostModelHistory(
            insurance_cost = insurance_cost,
            VIN = insurance_cost.VIN,
            accident = insurance_cost.accident,
            deductible = insurance_cost.deductible,
            currency = insurance_cost.currency,
            total_cost = insurance_cost.total_cost,
            modified_by = insurance_cost.modified_by,
            location=insurance_cost.location
        )