from api.Models.Cost.fuel_cost import FuelCost
from rest_framework.response import Response
from rest_framework import status
from api.Models.fuel_type import FuelType
from ..CurrencyManager.CurrencyHelper import CurrencyHelper
from ..MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from ..IssueManager.IssueHelper import IssueHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from .CostHelper import CurrencyConversionHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
from ..UserManager.UserHelper import UserHelper
from api.Models.asset_model import AssetModel
from core.AssetManager.AssetHelper import AssetHelper
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------------------------------

class GeneralCostUpdater():

    @staticmethod
    def set_cost_obj_location_by_VIN(cost_obj, vin, user):
        try:
            location = AssetHelper.get_asset_location_id(vin, user.db_access)
            cost_obj.location_id = location
            return cost_obj
        except Exception as e:
            Logger.getLogger().error(CustomError.LDE_0, e)
            return None

# ---------------------------------------------------------------------------------------------------------------------

class FuelUpdater():

    @staticmethod
    def create_fuel_type_entry(fuel_type_data, user):
        try:
            fuel_entry = FuelType(name=fuel_type_data.get("fuel_name").strip())
            return FuelUpdater.update_fuel_cost_created_by(fuel_entry, user)
        except Exception as e:
            Logger.getLogger().error(CustomError.FTCF_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FTCF_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_fuel_cost_created_by(fuel_cost_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            fuel_cost_request_obj.created_by = detailed_user
            fuel_cost_request_obj.modified_by = detailed_user
            return fuel_cost_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_7, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_7, e), status=status.HTTP_400_BAD_REQUEST)
            
# ---------------------------------------------------------------------------------------------------------------------

class FuelCardUpdater():

    @staticmethod
    def update_fuel_card_issuer(fuel_card_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            fuel_card_request_obj.issuer = detailed_user
            return fuel_card_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_16, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_16, e), status=status.HTTP_400_BAD_REQUEST)
            

# ---------------------------------------------------------------------------------------------------------------------

class LicenseUpdater():

    @staticmethod
    def update_license_cost_created_by(license_cost_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            license_cost_request_obj.created_by = detailed_user
            license_cost_request_obj.modified_by = detailed_user
            license_cost_request_obj.save()
            return license_cost_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_8, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_8, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

class RentalUpdater():

    @staticmethod
    def update_rental_cost_created_by(rental_cost_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            rental_cost_request_obj.created_by = detailed_user
            rental_cost_request_obj.modified_by = detailed_user
            return rental_cost_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_9, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_9, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

class LaborUpdater():

    @staticmethod
    def update_labor_cost_created_by(labor_cost_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            labor_cost_request_obj.created_by = detailed_user
            labor_cost_request_obj.modified_by = detailed_user
            labor_cost_request_obj.save()
            return labor_cost_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_10, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_10, e), status=status.HTTP_400_BAD_REQUEST)
       # ----------------------------------------------------------------------------------

    @staticmethod
    def update_labor_cost_fields(labor_obj, request_data, db_name):
        try:
            if not len(str(request_data.get("maintenance"))) == 0 and request_data.get("maintenance") is not None:
                maintenance_request, maintenance_request_response = MaintenanceHelper.get_maintenance_request_by_id(request_data.get("maintenance"), db_name)
                if maintenance_request_response.status_code != status.HTTP_302_FOUND:
                    return labor_obj, maintenance_request_response
                labor_obj.maintenance = maintenance_request

            if not len(str(request_data.get("issue"))) == 0 and request_data.get("issue") is not None:
                issue, issue_response = IssueHelper.get_issue_by_id(request_data.get("issue"), db_name)
                if issue_response.status_code != status.HTTP_302_FOUND:
                    return labor_obj, issue_response
                labor_obj.issue = issue

            if not len(str(request_data.get("disposal"))) == 0 and request_data.get("disposal") is not None:
                disposal_request, disposal_request_response = DisposalHelper.get_disposal_request_by_id(request_data.get("disposal"), db_name)
                if disposal_request_response.status_code != status.HTTP_302_FOUND:
                    return labor_obj, disposal_request_response
                labor_obj.disposal = disposal_request

            if not len(str(request_data.get("base_hourly_rate"))) == 0 and request_data.get("base_hourly_rate") is not None:
                labor_obj.base_hourly_rate = request_data.get("base_hourly_rate")

            if not len(str(request_data.get("total_base_hours"))) == 0 and request_data.get("total_base_hours") is not None:
                labor_obj.total_base_hours = request_data.get("total_base_hours")

            if not len(str(request_data.get("overtime_rate"))) == 0 and request_data.get("overtime_rate") is not None:
                labor_obj.overtime_rate = request_data.get("overtime_rate")

            if not len(str(request_data.get("total_overtime_hours"))) == 0 and request_data.get("total_overtime_hours") is not None:
                labor_obj.total_overtime_hours = request_data.get("total_overtime_hours")

            if not len(str(request_data.get("taxes"))) == 0 and request_data.get("taxes") is not None:
                labor_obj.taxes = request_data.get("taxes")

            if not len(str(request_data.get("total_cost"))) == 0 and request_data.get("total_cost") is not None:
                labor_obj.total_cost = request_data.get("total_cost")

            if not len(str(request_data.get("currency"))) == 0 and request_data.get("currency") is not None:
                labor_obj.currency = CurrencyHelper.get_currency_by_id(request_data.get("currency"), db_name)

            return labor_obj, Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_0, e))
            return labor_obj, Response(CustomError.get_full_error_json(CustomError.TUF_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

class PartsUpdater():
    
    @staticmethod
    def update_parts_created_by(parts_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            parts_request_obj.created_by = detailed_user
            parts_request_obj.modified_by = detailed_user
            parts_request_obj.save()
            return parts_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_11, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_11, e), status=status.HTTP_400_BAD_REQUEST) 

       # ----------------------------------------------------------------------------------

    @staticmethod
    def update_parts_fields(parts_obj, request_data, db_name):
        try:
            if not len(str(request_data.get("maintenance"))) == 0 and request_data.get("maintenance") is not None:
                maintenance_request, maintenance_request_response = MaintenanceHelper.get_maintenance_request_by_id(request_data.get("maintenance"), db_name)
                if maintenance_request_response.status_code != status.HTTP_302_FOUND:
                    return parts_obj, maintenance_request_response
                parts_obj.maintenance = maintenance_request

            if not len(str(request_data.get("issue"))) == 0 and request_data.get("issue") is not None:
                issue, issue_response = IssueHelper.get_issue_by_id(request_data.get("issue"), db_name)
                if issue_response.status_code != status.HTTP_302_FOUND:
                    return parts_obj, issue_response
                parts_obj.issue = issue

            if not len(str(request_data.get("disposal"))) == 0 and request_data.get("disposal") is not None:
                disposal_request, disposal_request_response = DisposalHelper.get_disposal_request_by_id(request_data.get("disposal"), db_name)
                if disposal_request_response.status_code != status.HTTP_302_FOUND:
                    return parts_obj, disposal_request_response
                parts_obj.disposal = disposal_request

            if not len(str(request_data.get("part_number"))) == 0 and request_data.get("part_number") is not None:
                parts_obj.part_number = request_data.get("part_number").strip()

            if not len(str(request_data.get("part_name"))) == 0 and request_data.get("part_name") is not None:
                parts_obj.part_name = request_data.get("part_name").strip()

            if not len(str(request_data.get("quantity"))) == 0 and request_data.get("quantity") is not None:
                parts_obj.quantity = request_data.get("quantity")

            if not len(str(request_data.get("price"))) == 0 and request_data.get("price") is not None:
                parts_obj.price = request_data.get("price")

            if not len(str(request_data.get("taxes"))) == 0 and request_data.get("taxes") is not None:
                parts_obj.taxes = request_data.get("taxes")

            if not len(str(request_data.get("total_cost"))) == 0 and request_data.get("total_cost") is not None:
                parts_obj.total_cost = request_data.get("total_cost")

            if not len(str(request_data.get("currency"))) == 0 and request_data.get("currency") is not None:
                parts_obj.currency = CurrencyHelper.get_currency_by_id(request_data.get("currency"), db_name)

            return parts_obj, Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_0, e))
            return parts_obj, Response(CustomError.get_full_error_json(CustomError.TUF_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

class InsuranceUpdater():

    @staticmethod
    def update_insurance_cost_created_by(insurance_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            insurance_obj.created_by = detailed_user
            insurance_obj.modified_by = detailed_user
            insurance_obj.save()
            return insurance_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_12, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_12, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

class AcquisitionUpdater():

    @staticmethod
    def update_acquisition_cost_created_by(acquisition_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            acquisition_obj.created_by = detailed_user
            acquisition_obj.modified_by = detailed_user
            acquisition_obj.save()
            return acquisition_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_12, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_12, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

class DeliveryUpdater():

    @staticmethod
    def update_delivery_cost_created_by(delivery_cost_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            delivery_cost_obj.created_by = detailed_user
            delivery_cost_obj.modified_by = detailed_user
            delivery_cost_obj.save()
            return delivery_cost_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_12, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_12, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------