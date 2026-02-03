
from core.LocationManager.LocationHelper import LocationHelper
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_request import AssetRequestModel
from api.Models.DetailedUser import DetailedUser
from ..UserManager.UserHelper import UserHelper
from ..BusinessUnitManager.BusinessUnitHelper import BusinessUnitHelper
from ..AssetRequestManager.AssetRequestHelper import AssetRequestHelper
from ..EquipmentTypeManager.EquipmentTypeHelper import EquipmentTypeHelper
from ..AssetRequestJustificationManager.AssetRequestJustificationHelper import AssetRequestJustificationHelper
from ..Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
from ..CostCentreManager.CostCentreHelper import CostCentreHelper

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetRequestUpdater():

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_asset_request_post_creation(asset_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            asset_request_obj.created_by = detailed_user
            asset_request_obj.modified_by = detailed_user
            asset_request_obj.custom_id = str(detailed_user.company.company_name).replace(' ', '-') + "-ar-" + str(asset_request_obj.id)
            asset_request_obj.save()
            return asset_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_1, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_1, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_asset_request_modified_by(asset_request_obj, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            asset_request_obj.modified_by = detailed_user
            asset_request_obj.save()
            return asset_request_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_1, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_1, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_asset_request_fields(asset_request_entry, request_data, user):
        try:
            is_important = False
            if not len(str(request_data.get("business_unit_id"))) == 0 and request_data.get("business_unit_id") is not None:
                business_unit, business_unit_response = BusinessUnitHelper.get_business_unit_by_id(request_data.get("business_unit_id"), user.db_access)
                if business_unit_response.status_code != status.HTTP_302_FOUND:
                    return asset_request_entry, business_unit_response
                asset_request_entry.business_unit = business_unit
            
            if request_data.get("cost_centre_id")!=None:
                cost_centre,cost_centre_response=CostCentreHelper.get_by_id(user.db_access,request_data.get("cost_centre_id"))
                if cost_centre_response.status_code!=status.HTTP_302_FOUND:
                    return asset_request_entry,cost_centre_response
                asset_request_entry.cost_centre=cost_centre
                
                # TODO: seems important to me (Will) but should verify, particularly since business unit isn't important?
                # note, this determines whether email is sent
                
                is_important=True
            
            if not len(str(request_data.get("equipment_type_id"))) == 0 and request_data.get("equipment_type_id") is not None:
                equipment_type, equipment_type_response = EquipmentTypeHelper.get_equipment_type_by_id(request_data.get("equipment_type_id"), user.db_access)
                if equipment_type_response.status_code != status.HTTP_302_FOUND:
                    return asset_request_entry, equipment_type_response
                asset_request_entry.equipment = equipment_type
                is_important = True
            
            if not len(str(request_data.get("justification_id"))) == 0 and request_data.get("justification_id") is not None:
                justification, justification_response = AssetRequestJustificationHelper.get_justification_by_id(request_data.get("justification_id"), user.db_access)
                if justification_response.status_code != status.HTTP_302_FOUND:
                    return asset_request_entry, justification_response
                asset_request_entry.justification = justification

            if not len(str(request_data.get("location_id"))) == 0 and request_data.get("location_id") is not None:
                location, location_response = LocationHelper.get_location_by_id(request_data.get("location_id"), user.db_access)
                if location_response.status_code != status.HTTP_302_FOUND:
                    return asset_request_entry, location_response
                asset_request_entry.location = location

            if not len(str(request_data.get("date_required"))) == 0 and request_data.get("date_required") is not None:
                asset_request_entry.date_required = HelperMethods.datetime_string_to_datetime(request_data.get("date_required"))
                is_important = True

            if not len(str(request_data.get("nonstandard_description"))) == 0 and request_data.get("nonstandard_description") is not None:
                asset_request_entry.nonstandard_description = request_data.get("nonstandard_description").strip()

            if not len(str(request_data.get("quantity"))) == 0 and request_data.get("quantity") is not None:
                asset_request_entry.quantity = request_data.get("quantity")
                is_important = True
                
            asset_request_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)        

            return asset_request_entry, is_important, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_1, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_1, e), status=status.HTTP_400_BAD_REQUEST)
