from rest_framework.response import Response
from rest_framework import status
from api.Models.Cost.parts_history import PartsModelHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class PartsHistory:

    @staticmethod
    def create_parts_record_by_obj(parts):
        try:
            parts_history_entry = PartsHistory.generate_parts_history_entry(parts)
            parts_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_parts_history_entry(parts):
        return PartsModelHistory(
                parts = parts,
                maintenance = parts.maintenance,
                issue = parts.issue,
                disposal = parts.disposal,
                part_number = parts.part_number,
                part_name = parts.part_name,
                quantity = parts.quantity,
                price = parts.price,
                taxes = parts.taxes,
                currency = parts.currency,
                total_cost = parts.total_cost,
                modified_by = parts.modified_by,
                location=parts.location
            )

