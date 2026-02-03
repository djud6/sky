from django.core.mail.message import sanitize_address
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_transfer import AssetTransfer
from api.Models.transfer_file import TransferFile
from ..UserManager.UserHelper import UserHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..LocationManager.LocationHelper import LocationHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class TransferUpdater():

    # --------------------------------------------------------------------------------------

    @staticmethod
    def create_transfer_request(request_data, user, sender_detailed_user):
        try:
            transfer_request_entry, transfer_request_response = TransferUpdater.create_transfer_request_entry(request_data, user, sender_detailed_user)
            if transfer_request_response.status_code != status.HTTP_201_CREATED:
                return None, transfer_request_response
            transfer_request_entry.save()
            return transfer_request_entry, Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def create_transfer_request_entry(request_data, user, sender_detailed_user):
        disposal = None
        if request_data.get("disposal") is not None:
            disposal, disposal_response = DisposalHelper.get_disposal_request_by_id(request_data.get("disposal"), user.db_access)
            if disposal_response.status_code != status.HTTP_302_FOUND:
                return None, disposal_response

        location, location_response = LocationHelper.get_location_by_id(request_data.get("destination_location"), user.db_access)
        if location_response.status_code != status.HTTP_302_FOUND:
            return None, location_response
    
        asset = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), user.db_access)

        return AssetTransfer(
            VIN=asset,
            destination_location=location,
            original_location=asset.current_location,
            justification=request_data.get("justification"),
            disposal=disposal,
            status=AssetTransfer.awaiting_approval,
            created_by=sender_detailed_user,
            modified_by=sender_detailed_user,
            latitude=AssetHelper.get_asset_by_VIN(request_data.get("VIN"), user.db_access).current_location.latitude,
            longitude=AssetHelper.get_asset_by_VIN(request_data.get("VIN"), user.db_access).current_location.longitude,
        ), Response(status=status.HTTP_201_CREATED)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_transfer_post_creation(transfer_obj, detailed_user):
        try:
            transfer_obj.custom_id = str(detailed_user.company.company_name).replace(' ', '-') + "-t-" + str(transfer_obj.asset_transfer_id)
            transfer_obj.save()
            return transfer_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.FSU_3, e)
            return None, Response(CustomError.get_full_error_json(CustomError.FSU_3, e), status=status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_transfer_status(transfer_obj, asset_obj, _status, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            transfer_obj.modified_by = detailed_user
            transfer_obj.status = _status
            transfer_obj.save()
            if _status=='delivered':
                asset_obj.current_location = transfer_obj.destination_location
                asset_obj.save()
            return transfer_obj, asset_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    # --------------------------------------------------------------------------------------

    @staticmethod
    def create_transfer_file_records(transfer_obj, file_infos, db_name):
        try:
            entries = list()
            for file_info in file_infos:
                entries.append(TransferUpdater.construct_transfer_file_instance(transfer_obj, file_info))
            TransferFile.objects.using(db_name).bulk_create(entries)

            return Response(status=status.HTTP_201_CREATED)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0, e))
            return Response(CustomError.get_full_error_json(CustomError.FUF_0, e), status=status.HTTP_400_BAD_REQUEST)


    # --------------------------------------------------------------------------------------

    @staticmethod
    def construct_transfer_file_instance(transfer_obj, file_info, file_purpose, detailed_user):
        return TransferFile(
            transfer=transfer_obj,
            file_type=file_info.file_type,
            file_name=file_info.file_name,
            file_url=file_info.file_url,
            bytes=file_info.bytes,
            file_purpose=file_purpose,
            created_by=detailed_user
        )
    
    # --------------------------------------------------------------------------------------

    @staticmethod
    def update_transfer(transfer_entry, request_data, user):
        try:
            is_important = False
            if not len(str(request_data.get("destination_location_id"))) == 0 and request_data.get("destination_location_id") is not None:
                destination_location, destination_location_response = LocationHelper.get_location_by_id(request_data.get("destination_location_id"), user.db_access)
                if destination_location_response.status_code != status.HTTP_302_FOUND:
                    return transfer_entry, destination_location_response
                transfer_entry.destination_location = destination_location
            if not len(str(request_data.get("disposal_id"))) == 0 and request_data.get("disposal_id") is not None:
                disposal, disposal_response = DisposalHelper.get_disposal_request_by_id(request_data.get("disposal_id"), user.db_access)
                if disposal_response.status_code != status.HTTP_302_FOUND:
                    return transfer_entry, disposal_response
                transfer_entry.disposal = disposal

            if not len(str(request_data.get("justification"))) == 0 and request_data.get("justification") is not None:
                transfer_entry.justification = request_data.get("justification").strip()
            if not len(str(request_data.get("longitude"))) == 0 and request_data.get("longitude") is not None:
                transfer_entry.longitude = request_data.get("longitude").strip()
            if not len(str(request_data.get("latitude"))) == 0 and request_data.get("latitude") is not None:
                transfer_entry.latitude = request_data.get("latitude").strip()
            if not len(str(request_data.get("pickup_date"))) == 0 and request_data.get("pickup_date") is not None:
                transfer_entry.pickup_date = HelperMethods.datetime_string_to_datetime(request_data.get("pickup_date"))
                is_important = True
            if not len(str(request_data.get("interior_condition"))) == 0 and request_data.get("interior_condition") is not None:
                transfer_entry.interior_condition = request_data.get("interior_condition").strip()
            if not len(str(request_data.get("interior_condition_details"))) == 0 and request_data.get("interior_condition_details") is not None:
                transfer_entry.interior_condition_details = request_data.get("interior_condition_details").strip()
            if not len(str(request_data.get("exterior_condition"))) == 0 and request_data.get("exterior_condition") is not None:
                transfer_entry.exterior_condition = request_data.get("exterior_condition").strip()
            if not len(str(request_data.get("exterior_condition_details"))) == 0 and request_data.get("exterior_condition_details") is not None:
                transfer_entry.exterior_condition_details = request_data.get("exterior_condition_details").strip()
            if not len(str(request_data.get("mileage"))) == 0 and request_data.get("mileage") is not None:
                transfer_entry.mileage = request_data.get("mileage")
            if not len(str(request_data.get("hours"))) == 0 and request_data.get("hours") is not None:
                transfer_entry.hours = request_data.get("hours")

            transfer_entry.modified_by = UserHelper.get_detailed_user_obj(user.email, user.db_access)        

            return transfer_entry, is_important, Response(status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_9, e))
            return None, is_important, Response(CustomError.get_full_error_json(CustomError.TUF_9, e), status=status.HTTP_400_BAD_REQUEST)