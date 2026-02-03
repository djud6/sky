from api.Models.Cost.acquisition_cost_history import AcquisitionCostModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AcquisitionCostHistory:

    @staticmethod
    def create_acquisition_cost_record_by_obj(acquisition_cost):
        try:
            acquisition_cost_history_entry = AcquisitionCostHistory.generate_acquisition_cost_history_entry(acquisition_cost)
            acquisition_cost_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_acquisition_cost_history_entry(acquisition_cost):
        
        return AcquisitionCostModelHistory(
            acquisition_cost = acquisition_cost,
            VIN = acquisition_cost.VIN,
            total_cost = acquisition_cost.total_cost,
            taxes = acquisition_cost.taxes,
            administrative_cost = acquisition_cost.administrative_cost,
            misc_cost = acquisition_cost.misc_cost,
            currency = acquisition_cost.currency,
            modified_by = acquisition_cost.modified_by,
            location = acquisition_cost.location
        )