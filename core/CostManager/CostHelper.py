from core.HistoryManager import LaborCostHistory
from rest_framework.response import Response
from rest_framework import status
from api.Models.Cost.fuel_cost import FuelCost
from api.Models.Cost.fuel_cost_history import FuelCostModelHistory
from api.Models.Cost.license_cost import LicenseCost
from api.Models.Cost.license_cost_history import LicenseCostModelHistory
from api.Models.Cost.rental_cost import RentalCost
from api.Models.Cost.rental_cost_history import RentalCostModelHistory
from api.Models.Cost.insurance_cost import InsuranceCost
from api.Models.Cost.insurance_cost_history import InsuranceCostModelHistory
from api.Models.Cost.acquisition_cost import AcquisitionCost
from api.Models.Cost.acquisition_cost_history import AcquisitionCostModelHistory
from api.Models.Cost.delivery_cost import DeliveryCost
from api.Models.Cost.delivery_cost_history import DeliveryCostHistory
from api.Models.Cost.labor_cost import LaborCost
from api.Models.Cost.labor_cost_history import LaborCostModelHistory
from api.Models.Cost.parts import Parts
from api.Models.Cost.parts_history import PartsModelHistory
from api.Models.Cost.currency import Currency
from api.Models.fuel_type import FuelType
from api.Models.fuel_card import FuelCard
from api.Models.accident_report import AccidentModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.asset_issue import AssetIssueModel
from ..CompanyManager.CompanyHelper import CompanyHelper
from ..CurrencyManager.CurrencyHelper import CurrencyHelper
from ..SnapshotManager.SnapshotHelper import SnapshotDailyCurrencyHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------------------------------

class FuelHelper():

    @staticmethod
    def select_related_to_fuel(qs):
        return qs.select_related('created_by', 'modified_by', 'fuel_type', 'currency')

    @staticmethod
    def get_fuel_type_by_name(fuel_name, db_name):
        try:
            return FuelType.objects.using(db_name).get(name=fuel_name), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.FTDNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.FTDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def fuel_type_exists(fuel_name, db_name):
        return FuelType.objects.using(db_name).filter(name=fuel_name).exists()
    
    @staticmethod
    def get_fuel_orders(db_name):
        return FuelCost.objects.using(db_name).all().order_by('-date_created')

    @staticmethod
    def get_fuel_cost_by_vin(vin, db_name):
        return FuelCost.objects.using(db_name).filter(VIN=vin).order_by('-date_created')
    
    @staticmethod
    def get_fuel_cost_by_id(fuel_id, db_name):
        return FuelCost.objects.using(db_name).filter(id=fuel_id)

    @staticmethod
    def get_fuel_cost_by_date_range(start_datetime, end_datetime, db_name):
        return FuelCost.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_fuel_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return FuelCostModelHistory.objects.using(db_name).filter(date__range=[start_datetime, end_datetime])

    @staticmethod
    def get_fuel_volume_in_liters(volume, unit):
        if str(unit).lower() == FuelCost.liter.lower():
            return volume
        if str(unit).lower() == FuelCost.gallon.lower():
            return volume * 3.78541
        else:
            return volume

# ---------------------------------------------------------------------------------------------------------------------

class LicenseHelper():
    
    @staticmethod
    def select_related_to_license(qs):
        return qs.select_related('created_by', 'modified_by', 'currency')

    @staticmethod
    def get_license_cost(db_name):
        return LicenseCost.objects.using(db_name).all().order_by('-date_created')

    @staticmethod
    def get_license_cost_by_vin(vin, db_name):
        return LicenseCost.objects.using(db_name).filter(VIN=vin).order_by('-date_created')

    @staticmethod
    def get_license_cost_by_date_range(start_datetime, end_datetime, db_name):
        return LicenseCost.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_license_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return LicenseCostModelHistory.objects.using(db_name).filter(date__range=[start_datetime, end_datetime])
    
# ---------------------------------------------------------------------------------------------------------------------

class RentalHelper():
    
    @staticmethod
    def select_related_to_rental(qs):
        return qs.select_related('created_by', 'modified_by', 'accident', 'maintenance', 'repair', 'currency')

    @staticmethod
    def get_rental_cost(db_name):
        return RentalCost.objects.using(db_name).all().order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_vin(vin, db_name):
        return RentalCost.objects.using(db_name).filter(Q(VIN=vin) | Q(accident__VIN=vin) |
        Q(maintenance__VIN=vin) | Q(repair__VIN=vin)).order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_accident_id(accident_id, db_name):
        return RentalCost.objects.using(db_name).filter(accident=accident_id).order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_maintenance_id(maintenance_id, db_name):
        return RentalCost.objects.using(db_name).filter(maintenance=maintenance_id).order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_repair_id(repair_id, db_name):
        return RentalCost.objects.using(db_name).filter(repair=repair_id).order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_accident_ids(accident_ids, db_name):
        return RentalCost.objects.using(db_name).filter(Q(accident__in=accident_ids)).select_related('location', 'accident').order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_maintenance_ids(maintenance_ids, db_name):
        return RentalCost.objects.using(db_name).filter(Q(maintenance__in=maintenance_ids)).select_related('location', 'accident').order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_repair_ids(repair_ids, db_name):
        return RentalCost.objects.using(db_name).filter(Q(repair__in=repair_ids)).select_related('location', 'accident').order_by('-date_created')

    @staticmethod
    def get_rental_cost_by_date_range(start_datetime, end_datetime, db_name):
        return RentalCost.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_rental_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return RentalCostModelHistory.objects.using(db_name).filter(date__range=[start_datetime, end_datetime])

    @staticmethod
    def get_rental_cost_obj_VIN(rental_cost_obj):
        if rental_cost_obj.VIN is not None:
            return rental_cost_obj.VIN
        elif rental_cost_obj.repair is not None:
            return rental_cost_obj.repair.VIN
        elif rental_cost_obj.maintenance is not None:
            return rental_cost_obj.maintenance.VIN
        elif rental_cost_obj.accident is not None:
            return rental_cost_obj.accident.VIN
        else:
            return None

# ---------------------------------------------------------------------------------------------------------------------

class LaborHelper():

    @staticmethod
    def select_related_to_labor(qs):
        return qs.select_related('created_by', 'modified_by', 'maintenance', 'issue', 'disposal', 'currency')

    @staticmethod
    def get_labor_cost(db_name):
        return LaborCost.objects.using(db_name).all().order_by('-date_created')

    @staticmethod
    def get_labor_obj_by_id(labor_id, db_name):
        return LaborCost.objects.using(db_name).get(id=labor_id)

    @staticmethod
    def get_labor_cost_by_vin(vin, db_name):
        return LaborCost.objects.using(db_name).filter(Q(maintenance__VIN=vin) |
        Q(issue__VIN=vin) | Q(disposal__VIN=vin)).order_by('-date_created')

    @staticmethod
    def get_labor_cost_by_maintenance_id(maintenance_id, db_name):
        return LaborCost.objects.using(db_name).filter(maintenance=maintenance_id).order_by('-date_created')

    @staticmethod
    def get_labor_cost_by_maintenance_ids(maintenance_ids, db_name):
        return LaborCost.objects.using(db_name).select_related('location', 'maintenance').filter(Q(maintenance__in=maintenance_ids)).order_by('-date_created')
    
    @staticmethod
    def get_labor_cost_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name):
        return LaborCost.objects.using(db_name).filter(Q(maintenance__in=maintenance_ids) | Q(issue__repair_id__in=repair_ids))

    @staticmethod
    def get_labor_cost_by_issue_id(issue_id, db_name):
        return LaborCost.objects.using(db_name).filter(issue=issue_id).order_by('-date_created')

    @staticmethod
    def get_labor_cost_by_issue_ids(issue_ids, db_name):
        return LaborCost.objects.using(db_name).filter(Q(issue__in=issue_ids)).select_related('location', 'issue').order_by('-date_created')

    @staticmethod
    def get_labor_cost_by_issue_id_list(issue_id_list, db_name):
        return LaborCost.objects.using(db_name).filter(issue__in=issue_id_list).order_by('-date_created')

    @staticmethod
    def get_labor_cost_by_disposal_id(disposal_id, db_name):
        return LaborCost.objects.using(db_name).filter(disposal=disposal_id).order_by('-date_created')

    @staticmethod
    def get_labor_cost_by_date_range(start_datetime, end_datetime, db_name):
        return LaborCost.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_labor_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return LaborCostModelHistory.objects.using(db_name).filter(date_modified__range=[start_datetime, end_datetime])

    @staticmethod
    def get_related_maintenance(_vin, db_name):
        try:
            maintenance_id_in_maintenance = MaintenanceRequestModel.objects.using(db_name).filter(VIN=_vin).values_list('maintenance_id', flat=True)
            maintenance_in_labor_cost = LaborCost.objects.using(db_name).filter(maintenance_id__in=maintenance_id_in_maintenance).order_by('-date_created')
            return maintenance_in_labor_cost
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_related_issues(_vin, db_name):
        try:
            issue_id_in_assetissue = AssetIssueModel.objects.using(db_name).filter(VIN=_vin).values_list('issue_id', flat=True)
            issue_in_labor_cost = LaborCost.objects.using(db_name).filter(issue_id__in=issue_id_in_assetissue).order_by('-date_created')
            return issue_in_labor_cost
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_labor_cost_obj_VIN(labor_obj):
        if labor_obj.issue is not None:
            return labor_obj.issue.VIN
        elif labor_obj.maintenance is not None:
            return labor_obj.maintenance.VIN
        elif labor_obj.disposal is not None:
            return labor_obj.disposal.VIN
        else:
            return None

    # This method assumes that issue, maintenance, and disposal are at index 1, 2, 3 respectively.
    @staticmethod
    def get_labor_cost_values_list_VIN(labor_values_list):
        index = 1
        while index <= 3:
            if labor_values_list[index] is not None:
                return labor_values_list[index]
            index += 1
        return None

# ---------------------------------------------------------------------------------------------------------------------

class PartsHelper():
    
    @staticmethod
    def select_related_to_parts(qs):
        return qs.select_related('created_by', 'modified_by', 'maintenance', 'issue', 'disposal', 'currency')

    @staticmethod
    def get_parts_by_maintenance(maintenance_id, db_name):
        return Parts.objects.using(db_name).filter(maintenance=maintenance_id).order_by('-date_created')

    @staticmethod
    def get_parts_by_maintenance_ids(maintenance_ids, db_name):
        return Parts.objects.using(db_name).filter(Q(maintenance__in=maintenance_ids)).select_related('location', 'maintenance').order_by('-date_created')

    @staticmethod
    def get_parts_obj_by_id(part_id, db_name):
        return Parts.objects.using(db_name).get(id=part_id)

    @staticmethod
    def get_parts_by_disposal(asset_disposal_id, db_name):
        return Parts.objects.using(db_name).filter(disposal=asset_disposal_id).order_by('-date_created')

    @staticmethod
    def get_parts_by_issue(asset_issue_id, db_name):
        return Parts.objects.using(db_name).filter(issue=asset_issue_id).order_by('-date_created')

    @staticmethod
    def get_parts_by_issue_list(asset_issue_list, db_name):
        return Parts.objects.using(db_name).filter(issue__in=asset_issue_list).select_related('location', 'issue').order_by('-date_created')

    @staticmethod
    def get_parts_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name):
        return Parts.objects.using(db_name).filter(Q(maintenance__in=maintenance_ids) | Q(issue__repair_id__in=repair_ids))

    @staticmethod
    def get_parts_by_number(part_number, db_name):
        return Parts.objects.using(db_name).filter(part_number=part_number).order_by('-date_created')

    @staticmethod
    def get_parts(db_name):
        return Parts.objects.using(db_name).all().order_by('-date_created')

    @staticmethod
    def get_parts_by_vin(vin, db_name):
        return Parts.objects.using(db_name).filter(Q(maintenance__VIN=vin) | Q(issue__VIN=vin) |
        Q(disposal__VIN=vin)).order_by('-date_created')
        
    @staticmethod
    def get_parts_cost_by_date_range(start_datetime, end_datetime, db_name):
        return Parts.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_parts_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return PartsModelHistory.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def part_number_exists(part_number, db_name):
        return Parts.objects.using(db_name).filter(part_number=part_number).exists()

    @staticmethod
    def get_related_maintenance(_vin, db_name):
        try:
            maintenance_id_in_maintenance = MaintenanceRequestModel.objects.using(db_name).filter(VIN=_vin).values_list('maintenance_id', flat=True)
            maintenance_in_parts =  Parts.objects.using(db_name).filter(maintenance_id__in=maintenance_id_in_maintenance).order_by('-date_created')
            return maintenance_in_parts
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_related_issues(_vin, db_name):
        try:
            issue_id_in_assetissue = AssetIssueModel.objects.using(db_name).filter(VIN=_vin).values_list('issue_id', flat=True)
            issue_in_parts = Parts.objects.using(db_name).filter(issue_id__in=issue_id_in_assetissue).order_by('-date_created')
            return issue_in_parts
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_related_disposal(_vin, db_name):
        try:
            disposal_id_in_disposalissue = AssetIssueModel.objects.using(db_name).filter(VIN=_vin).values_list('issue_id', flat=True)
            disposal_in_parts = Parts.objects.using(db_name).filter(disposal_id__in=disposal_id_in_disposalissue).order_by('-date_created')
            return disposal_in_parts
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_parts_cost_obj_VIN(parts_obj):
        if parts_obj.issue is not None:
            return parts_obj.issue.VIN
        elif parts_obj.maintenance is not None:
            return parts_obj.maintenance.VIN
        elif parts_obj.disposal is not None:
            return parts_obj.disposal.VIN
        else:
            return None

    # This method assumes that issue, maintenance, and disposal are at index 1, 2, 3 respectively.
    @staticmethod
    def get_parts_cost_values_list_VIN(parts_values_list):
        index = 1
        while index <= 3:
            if parts_values_list[index] is not None:
                return parts_values_list[index]
            index += 1
        return None
    
# ---------------------------------------------------------------------------------------------------------------------

class InsuranceHelper():

    @staticmethod
    def select_related_to_Insurance(qs):
        return qs.select_related('created_by', 'modified_by', 'accident', 'currency')

    @staticmethod
    def get_insurance_cost_by_accident_ID(accident_id, db_name):
        return InsuranceCost.objects.using(db_name).filter(accident=accident_id).order_by('-date_created')

    @staticmethod
    def get_insurance_cost_by_accident_ids(accident_ids, db_name):
        return InsuranceCost.objects.using(db_name).filter(Q(accident__in=accident_ids)).select_related('location', 'accident').order_by('-date_created')

    @staticmethod
    def get_insurance_cost_list(db_name):
        return InsuranceCost.objects.using(db_name).all().order_by('-date_created')

    @staticmethod
    def get_insurance_cost_by_vin(vin, db_name):
        return InsuranceCost.objects.using(db_name).filter(Q(VIN=vin) | Q(accident__VIN=vin)).order_by('-date_created')

    @staticmethod
    def get_insurance_cost_by_date_range(start_datetime, end_datetime, db_name):
        return InsuranceCost.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_insurance_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return InsuranceCostModelHistory.objects.using(db_name).filter(date__range=[start_datetime, end_datetime])

    @staticmethod
    def get_insurance_cost_obj_VIN(insurance_cost_obj):
        if insurance_cost_obj.VIN is not None:
            return insurance_cost_obj.VIN
        elif insurance_cost_obj.accident is not None:
            return insurance_cost_obj.accident.VIN
        else:
            return None

# ---------------------------------------------------------------------------------------------------------------------

class AcquisitionHelper():

    @staticmethod
    def select_related_to_acquisition(qs):
        return qs.select_related('created_by', 'modified_by', 'currency')
        
    @staticmethod
    def get_acquisition_cost_list(db_name):
        return AcquisitionCost.objects.using(db_name).all().order_by('-date_created')

    @staticmethod
    def get_acquisition_cost_by_vin(vin, db_name):
        return AcquisitionCost.objects.using(db_name).filter(VIN=vin)

    @staticmethod
    def get_acquisition_cost_by_date_range(start_datetime, end_datetime, db_name):
        return AcquisitionCost.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_acquisition_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return AcquisitionCostModelHistory.objects.using(db_name).filter(date__range=[start_datetime, end_datetime])

# ---------------------------------------------------------------------------------------------------------------------

class DeliveryHelper:

    @staticmethod
    def select_related_to_delivery(qs):
        return qs.select_related('created_by', 'modified_by', 'currency', 'maintenance', 'repair', 'disposal', 'asset_request')
        
    @staticmethod
    def get_delivery_cost_obj_VIN(delivery_cost_obj):
        if delivery_cost_obj.repair is not None:
            return delivery_cost_obj.repair.VIN
        elif delivery_cost_obj.maintenance is not None:
            return delivery_cost_obj.maintenance.VIN
        elif delivery_cost_obj.disposal is not None:
            return delivery_cost_obj.disposal.VIN
        elif delivery_cost_obj.asset_request.VIN is not None:
            return delivery_cost_obj.asset_request.VIN
        else:
            return None

    @staticmethod
    def get_delivery_cost_by_maintenance(maintenance_id, db_name):
        return DeliveryCost.objects.using(db_name).filter(maintenance=maintenance_id).order_by('-date_created')

    @staticmethod
    def get_delivery_cost_by_maintenance_ids(maintenance_ids, db_name):
        return DeliveryCost.objects.using(db_name).filter(maintenance__in=maintenance_ids).select_related('location', 'maintenance').order_by('-date_created')

    @staticmethod
    def get_delivery_cost_by_repair(repair_id, db_name):
        return DeliveryCost.objects.using(db_name).filter(repair=repair_id).order_by('-date_created')

    @staticmethod
    def get_delivery_cost_by_repair_list(repairs, db_name):
        return DeliveryCost.objects.using(db_name).filter(repair__in=repairs).select_related('location', 'repair').order_by('-date_created')

    @staticmethod
    def get_delivery_cost_by_asset_request(asset_request_id, db_name):
        return DeliveryCost.objects.using(db_name).filter(asset_request=asset_request_id).order_by('-date_created')

    @staticmethod
    def get_delivery_cost_by_disposal(disposal_id, db_name):
        return DeliveryCost.objects.using(db_name).filter(disposal=disposal_id).order_by('-date_created')

    @staticmethod
    def get_delivery_cost_by_vin(vin, db_name):
        return DeliveryCost.objects.using(db_name).filter(Q(maintenance__VIN=vin) |
        Q(repair__VIN=vin) | Q(disposal__VIN=vin) | Q(asset_request__VIN=vin)).order_by('-date_created')

    @staticmethod
    def get_delivery_costs(db_name):
        return DeliveryCost.objects.using(db_name).all().order_by('-date_created')
    
    @staticmethod
    def get_delivery_cost_by_date_range(start_datetime, end_datetime, db_name):
        return DeliveryCost.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

    @staticmethod
    def get_delivery_cost_history_by_date_range(start_datetime, end_datetime, db_name):
        return DeliveryCostHistory.objects.using(db_name).filter(date_created__range=[start_datetime, end_datetime])

# ---------------------------------------------------------------------------------------------------------------------

class UnitChoicesHelper():

    @staticmethod
    def select_related_to_fueltype(qs):
        return qs.select_related('created_by', 'modified_by')

    @staticmethod
    def get_all_fuel_types(db_name):
        return FuelType.objects.using(db_name).all()

    @staticmethod
    def get_all_currency_types(db_name):
        return Currency.objects.using(db_name).all()
    
    @staticmethod
    def get_all_volume_units_types():
        return [x[1] for x in FuelCost.volume_unit_choices]

# ---------------------------------------------------------------------------------------------------------------------

class InvoiceHelper():
 
    @staticmethod
    def recognize_invoice_content(form_recognizer_client, files):

            poller = form_recognizer_client.begin_recognize_invoices(invoice=files, locale="en-US", content_type = files.content_type)
            invoices = poller.result()

            response_data = {}
            item_data = {}
            items_dict = {}
            count = 1

            for idx, invoice in enumerate(invoices):
                for k, v in invoice.fields.items():
                    if str(k) == "Items":
                        for idx, item in enumerate(invoice.fields.get("Items").value):
                            for i in item.value:
                                if item.value[i].confidence > 0.5:
                                    item_data[item.value[i].name] = item.value[i].value
                            items_dict["Item-"+str(count)] = item_data
                            item_data = {}
                            count+=1
                    else:
                        invoice_field = invoice.fields.get(str(k))
                        if invoice_field.confidence > 0.5:
                            response_data[invoice_field.name] = invoice_field.value
            
            response_data["Items"] = items_dict
            return response_data

# ---------------------------------------------------------------------------------------------------------------------

class CurrencyConversionHelper():

    @staticmethod
    def convert_currency_request_data(request_data, currency_fields, db_name):
            input_currency_id = request_data.get("currency")
            standard_currency = CompanyHelper.get_list_companies(db_name)[0].standard_currency

            if standard_currency == None:
                # set to USD
                standard_currency = CurrencyHelper.get_currency_by_code("USD", db_name)
            
            # check if currency exists in the database
            try:
                input_currency = CurrencyHelper.get_currency_by_id(input_currency_id, db_name)
            except Exception as e:
                return None

            # conversion rate from input to standard
            rate = SnapshotDailyCurrencyHelper.get_snapshot_currency(standard_currency.code, db_name).currency_value / SnapshotDailyCurrencyHelper.get_snapshot_currency(input_currency.code, db_name).currency_value
            
            # multiply each value in the currency fields by conversion rate
            for field in currency_fields:
                if field in request_data.keys():
                    request_data[field] = float(request_data[field]) * rate

            request_data["currency"] = standard_currency.id

            return request_data

# ---------------------------------------------------------------------------------------------------------------------

class FuelCardHelper():
    
    @staticmethod
    def get_fuel_cards(db_name):
        return FuelCard.objects.using(db_name).all()

    @staticmethod
    def get_fuel_cards_by_business_unit(business_unit_id, db_name):
        return FuelCard.objects.using(db_name).filter(business_unit__pk=business_unit_id)
    
    @staticmethod
    def get_fuel_card_by_card_id(card_id, db_name):
        return FuelCard.objects.using(db_name).filter(card_id=card_id).first()

# ---------------------------------------------------------------------------------------------------------------------
