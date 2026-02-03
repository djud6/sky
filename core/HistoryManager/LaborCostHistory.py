from rest_framework.response import Response
from rest_framework import status
from api.Models.Cost.labor_cost_history import LaborCostModelHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class LaborHistory:

    @staticmethod
    def create_labor_cost_record_by_obj(labor_cost):
        try:
            labor_cost_history_entry = LaborHistory.generate_labor_cost_history_entry(labor_cost)
            labor_cost_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_labor_cost_history_entry(labor_cost):
        return LaborCostModelHistory(
                labor = labor_cost,
                maintenance = labor_cost.maintenance,
                issue = labor_cost.issue,
                disposal = labor_cost.disposal,
                base_hourly_rate = labor_cost.base_hourly_rate,
                total_base_hours = labor_cost.total_base_hours,
                overtime_rate = labor_cost.overtime_rate,
                total_overtime_hours = labor_cost.total_overtime_hours,
                taxes = labor_cost.taxes,
                currency = labor_cost.currency,
                total_cost = labor_cost.total_cost,
                modified_by = labor_cost.modified_by,
                location=labor_cost.location
            )