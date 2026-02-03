from rest_framework.response import Response
from rest_framework import status
from api.Models.DetailedUser import DetailedUser
from core.AssetTypeChecksManager.AssetTypeChecksUpdater import AssetTypeChecksUpdater
from core.AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from core.AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from core.HistoryManager.AssetTypeChecksHistory import AssetTypeChecksHistory
from api.Models.asset_type_checks import AssetTypeChecks
from api.Serializers.serializers import AssetTypeChecksSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

from core.AssetTypeManager.AssetTypeUpdater import AssetTypeUpdater
from core.UserManager.UserHelper import UserHelper

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeChecksHandler():

    @staticmethod
    def handle_add_asset_type_checks(request_data, user):
        try:
            # check if asset type exists
            asset_type_obj, asset_type_response = AssetTypeHelper.get_asset_type_by_name(request_data.get('asset_type_name'), user.db_access)
            if asset_type_response.status_code != status.HTTP_302_FOUND:
                return asset_type_response

            # update input data
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            updated_data = AssetTypeChecksHelper.update_asset_type_check_dict(request_data, detailed_user)

            # add checks for asset type
            ser = AssetTypeChecksSerializer(data=updated_data)
            if ser.is_valid():
                checks_obj = ser.save()
                checks_obj = AssetTypeChecksUpdater.update_header_fields(checks_obj, checks_obj.__dict__)
                checks_obj.save()
                AssetTypeUpdater.update_asset_type_checks_fk(asset_type_obj, checks_obj)

                # add asset type checks record
                history_response = AssetTypeChecksHistory.create_asset_type_checks_record_by_obj(checks_obj)
                if history_response.status_code != status.HTTP_201_CREATED:
                    return history_response

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def handle_update_asset_type_checks(request_data, user):
        try:
            # check if asset type check exists
            if not AssetTypeChecksHelper.asset_type_checks_exist_by_id(request_data.get('asset_type_checks_id'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.ATNDNE_1))
                return Response(CustomError.get_full_error_json(CustomError.ATNDNE_1), status=status.HTTP_400_BAD_REQUEST)

            # get asset type checks object
            checks_obj = AssetTypeChecksHelper.get_checks_by_id(request_data.get('asset_type_checks_id'), user.db_access)

            # edit asset type checks
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            updated_checks_obj, update_response = AssetTypeChecksUpdater.update_asset_type_checks_fields(checks_obj, request_data, detailed_user)
            if update_response.status_code != status.HTTP_202_ACCEPTED:
                return update_response

            # add asset type checks record
            history_response = AssetTypeChecksHistory.create_asset_type_checks_record_by_obj(checks_obj)
            if history_response.status_code != status.HTTP_201_CREATED:
                return history_response

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)