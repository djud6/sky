from api.Models.Cost.delivery_cost_history import DeliveryCostHistory as DeliveryCostModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DeliveryCostHistory:

    @staticmethod
    def create_delivery_cost_record_by_obj(delivery_cost):
        try:
            delivery_cost_history_entry = DeliveryCostHistory.generate_delivery_cost_history_entry(delivery_cost)
            delivery_cost_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_delivery_cost_history_entry(delivery_cost):
        
        return DeliveryCostModelHistory(
            delivery_cost = delivery_cost,
            maintenance = delivery_cost.maintenance,
            repair = delivery_cost.repair,
            disposal = delivery_cost.disposal,
            asset_request = delivery_cost.asset_request,
            price = delivery_cost.price,
            taxes = delivery_cost.taxes,
            currency = delivery_cost.currency,
            total_cost = delivery_cost.total_cost,
            modified_by = delivery_cost.modified_by,
            location = delivery_cost.location
        )