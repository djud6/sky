from multiprocessing import managers
import statistics
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from core.PaymentManager.PaymentHelper import PaymentHelper
from core.PaymentManager.PaymentUpdater import PaymentUpdater
from core.AnalyticsManager.AnalyticsHandler import AnalyticsHandler
from core.FileManager.FileHelper import FileHelper
from core.CompanyManager.CompanyHelper import CompanyHelper
from core.HistoryManager.PricingRatesHistory import PricingRatesHistoryUpdater
from core.HistoryManager.InvoiceLogHistory import InvoiceLogHistoryUpdater
from core.Helper import HelperMethods
import numbers
from datetime import datetime
from payment.Serializers.serializers import PricingRatesSerializer, InvoiceLogSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class PaymentHandler():

    @staticmethod
    def handle_add_pricing_rate(request_data, db_name):
        try:
            # Check currency code
            if not PaymentHelper.is_pricing_rate_currency_valid(request_data.get('currency_code')):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.CDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            request_data['company_id'] = db_name
            pricing_rates_entry = PaymentUpdater.create_pricing_rates_entry(request_data)
            pricing_rates_entry.save(using='payment')

            # create pricing rates record
            if not PricingRatesHistoryUpdater.create_pricing_rates_record_by_obj(pricing_rates_entry):
                Logger.getLogger().error(CustomError.MHF_19)
                return Response(CustomError.get_full_error_json(CustomError.MHF_19), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_pricing_rates(request_data, company_id):
        try:
            pricing_rates, response = PaymentHelper.get_pricing_rates_by_company_id(company_id)
            if response.status_code != status.HTTP_302_FOUND:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.PRDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.PRDNE_0), status=status.HTTP_400_BAD_REQUEST)

            updated_pricing_rates, response = PaymentUpdater.update_pricing_rates_fields(pricing_rates, request_data)
            if response.status_code != status.HTTP_202_ACCEPTED:
                return response

            updated_pricing_rates.save(using='payment')

            # create pricing rates record
            if(not PricingRatesHistoryUpdater.create_pricing_rates_record_by_obj(updated_pricing_rates)):
                Logger.getLogger().error(CustomError.MHF_19)
                return Response(CustomError.get_full_error_json(CustomError.MHF_19), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_list_pricing_rates():
        try:
            pricing_rates = PaymentHelper.get_all_pricing_rates()
            ser = PricingRatesSerializer(pricing_rates, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_pricing_rates_by_company_id(company_id):
        try:
            pricing_rates, response = PaymentHelper.get_pricing_rates_by_company_id(company_id)
            if response.status_code != status.HTTP_302_FOUND:
                return response
            ser = PricingRatesSerializer(pricing_rates)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_create_invoice_for_daterange(request_data):
        try:
            company_id = request_data.get('company_id')
            start_date = HelperMethods.naive_to_aware_utc_datetime(HelperMethods.date_string_to_datetime(request_data.get('start_date')))
            end_date = HelperMethods.naive_to_aware_utc_datetime(HelperMethods.date_string_to_datetime(request_data.get('end_date')))
            tax_percentage = request_data.get('tax_percentage')

            # Check tax percentage validity
            if not isinstance(tax_percentage, numbers.Number) or tax_percentage < 0:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.I_0))
                return Response(CustomError.get_full_error_json(CustomError.I_0), status=status.HTTP_400_BAD_REQUEST)

            pricing_rates, response = PaymentHelper.get_pricing_rates_by_company_id(company_id)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            # counts
            asset_user_counts = AnalyticsHandler.handle_max_users_and_assets_for_daterange(start_date, end_date, company_id).data
            asset_cost = HelperMethods.round_to_sig_digs(asset_user_counts.get('max_assets') * pricing_rates.rate_per_asset, 3)
            user_cost = HelperMethods.round_to_sig_digs(asset_user_counts.get('max_users') * pricing_rates.rate_per_user, 3)

            # data usage
            data_usage = AnalyticsHandler.handle_data_per_asset_for_daterange(start_date, end_date, company_id).data
            data_cost = HelperMethods.round_to_sig_digs((data_usage.get('total_kilobytes') / 100000) * pricing_rates.data_overrage_fee, 3)

            sub_total_cost = HelperMethods.round_to_sig_digs(asset_cost + user_cost + data_cost, 3)
            tax_cost = (tax_percentage / 100) * sub_total_cost

            # make entry to invoice log table
            invoice_log_data = {
                'company_id': pricing_rates.company_id,
                'total_billed_for_users': user_cost,
                'total_billed_for_assets': asset_cost,
                'total_billed_for_overrage_fees': data_cost,
                'total_tax': tax_cost, 
                'currency_code': pricing_rates.currency_code,
                'payment_due_date': HelperMethods.add_time_to_datetime(datetime.now(), 30, time_unit='days')
            }
            invoice_log_entry = PaymentUpdater.create_invoice_log_entry(invoice_log_data)
            invoice_log_entry.save(using='payment')

            # create invoice log record
            if(not InvoiceLogHistoryUpdater.create_invoice_log_record_by_obj(invoice_log_entry)):
                Logger.getLogger().error(CustomError.MHF_20)
                return Response(CustomError.get_full_error_json(CustomError.MHF_20), status=status.HTTP_400_BAD_REQUEST)

            client_company = CompanyHelper.get_list_companies(pricing_rates.company_id)[0]

            invoice_pdf_data = {
                'tax_percentage': tax_percentage,
                'sub_total_cost': sub_total_cost,
                'total_cost': sub_total_cost + tax_cost,
                'user_price': pricing_rates.rate_per_user,
                'asset_price': pricing_rates.rate_per_asset,
                'data_price': pricing_rates.data_overrage_fee,
                'max_users': asset_user_counts.get('max_users'),
                'max_assets': asset_user_counts.get('max_assets'),
                'data_amount': HelperMethods.round_to_sig_digs((data_usage.get('total_kilobytes') / 100000), 3), 
                'company_name': client_company.company_name,
                'company_address': client_company.company_address,
                'company_phone': client_company.company_phone,
                'accounting_email': client_company.accounting_email,
                'invoice_log_id': str(invoice_log_entry.id).zfill(7),
                'date': str(start_date.date()) + ' - ' + str(end_date.date()),
                'payment_due_date': str(invoice_log_entry.payment_due_date.date()),
                'currency_code': invoice_log_entry.currency_code
            }

            template_location = str(HelperMethods.GetProjectRoot()) + "/payment/templates/payment/invoice_template.html"
            pdf = FileHelper.render_to_pdf(template_location, {**invoice_log_data, **invoice_pdf_data})
            response = HttpResponse(pdf, content_type='application/pdf', status=status.HTTP_201_CREATED)
            filename = "invoice-" + str(invoice_log_entry.id).zfill(7) + ".pdf"
            content = "attachment; filename=" + filename
            response["Content-Disposition"] = content
            return response

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_invoice_log_is_paid(request_data):
        try:
            invoice_log_id = request_data.get('invoice_log_id')
            is_paid = HelperMethods.validate_bool(request_data.get('is_paid'))

            # get invoice log entry
            invoice_log_entry, response = PaymentHelper.get_invoice_log_by_id(invoice_log_id)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            invoice_log_entry.is_paid = is_paid
            invoice_log_entry.save(using='payment')

            # create invoice log record
            if(not InvoiceLogHistoryUpdater.create_invoice_log_record_by_obj(invoice_log_entry)):
                Logger.getLogger().error(CustomError.MHF_20)
                return Response(CustomError.get_full_error_json(CustomError.MHF_20), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_list_invoice_logs():
        try:
            invoice_logs = PaymentHelper.get_all_invoice_logs()
            ser = InvoiceLogSerializer(invoice_logs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_invoice_logs_by_company_id(company_id):
        try:
            invoice_logs = PaymentHelper.get_invoice_logs_by_company_id(company_id)
            ser = InvoiceLogSerializer(invoice_logs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_invoice_log_by_id(invoice_log_id):
        try:
            invoice_log, response = PaymentHelper.get_invoice_log_by_id(invoice_log_id)
            if response.status_code != status.HTTP_302_FOUND:
                return response
            ser = InvoiceLogSerializer(invoice_log)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)