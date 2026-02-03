from api.Models.Cost.rental_cost_history import RentalCostModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RentalCostHistory:

    @staticmethod
    def create_rental_cost_record_by_obj(rental_cost):
        try:
            rental_cost_history_entry = RentalCostHistory.generate_rental_cost_history_entry(rental_cost)
            rental_cost_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_rental_cost_history_entry(rental_cost):
        return RentalCostModelHistory(
            rental_cost = rental_cost,
            VIN = rental_cost.VIN,
            accident = rental_cost.accident,
            maintenance = rental_cost.maintenance,
            repair = rental_cost.repair,
            total_cost = rental_cost.total_cost,
            currency = rental_cost.currency,
            modified_by = rental_cost.modified_by,
            location=rental_cost.location 
        )