from rest_framework.response import Response
from rest_framework import status
from payment.Models.invoice_log_history import InvoiceLogHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class InvoiceLogHistoryUpdater():

    @staticmethod
    def create_invoice_log_record(invoice_log_id, db_name):
        try:
            invoice_log = InvoiceLogHistoryUpdater.objects.using(db_name).get(id=invoice_log_id)
            invoice_log_history_entry = InvoiceLogHistoryUpdater.generate_invoice_log_history_entry(invoice_log)
            invoice_log_history_entry.save(using='payment')
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_invoice_log_record_by_obj(invoice_log):
        try:
            invoice_log_history_entry = InvoiceLogHistoryUpdater.generate_invoice_log_history_entry(invoice_log)
            invoice_log_history_entry.save(using='payment')
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_invoice_log_history_entry(invoice_log):
        return InvoiceLogHistory(
            invoice_log=invoice_log,
            company_id=invoice_log.company_id,
            total_billed_for_users=invoice_log.total_billed_for_users,
            total_billed_for_assets=invoice_log.total_billed_for_assets,
            total_billed_for_overrage_fees=invoice_log.total_billed_for_overrage_fees,
            total_tax=invoice_log.total_tax,
            currency_code=invoice_log.currency_code,
            payment_due_date=invoice_log.payment_due_date,
            is_paid=invoice_log.is_paid
        )