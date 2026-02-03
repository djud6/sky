from api.Models.Cost.fuel_cost_history import FuelCostModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class FuelCostHistory:

    @staticmethod
    def create_fuel_cost_record_by_obj(fuel_cost, is_serialized):
        try:
            fuel_cost_history_entry = FuelCostHistory.generate_fuel_cost_history_entry(fuel_cost, is_serialized)
            fuel_cost_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_fuel_cost_history_entry(fuel_cost, is_serialized):
        if is_serialized:
            return FuelCostModelHistory(
                fuel_cost=fuel_cost,
                VIN=fuel_cost.VIN,
                fuel_type=fuel_cost.fuel_type,
                volume=fuel_cost.volume,
                volume_unit=fuel_cost.volume_unit,
                total_cost=fuel_cost.total_cost,
                taxes=fuel_cost.taxes,
                currency=fuel_cost.currency,
                location=fuel_cost.location,
                modified_by=fuel_cost.modified_by
            )
        else:
            return FuelCostModelHistory(
                fuel_cost=fuel_cost,
                VIN=fuel_cost.VIN,
                fuel_type=fuel_cost.fuel_type,
                volume=fuel_cost.volume,
                volume_unit=fuel_cost.volume_unit,
                total_cost=fuel_cost.total_cost,
                taxes=fuel_cost.taxes,
                currency=fuel_cost.currency,
                location=fuel_cost.location,
                modified_by=fuel_cost.modified_by
            )
