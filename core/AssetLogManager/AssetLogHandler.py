from rest_framework.response import Response
from rest_framework import status
from .AssetLogHelper import AssetLogHelper
from .AssetLogUpdater import AssetLogUpdater
from ..AssetManager.AssetHelper import AssetHelper
from ..Helper import HelperMethods
from api.Models.asset_log import AssetLog
from api.Serializers.serializers import AssetLogSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetLogHandler():

    @staticmethod
    def handle_add_asset_comment(request_data, user):

        if not AssetHelper.check_asset_status_active(request_data.get("VIN"), user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        ser = AssetLogSerializer(data=request_data)
        if ser.is_valid():
            asset_log_obj, creation_response = AssetLogUpdater.create_asset_log_comment(request_data, user)
            if creation_response.status_code != status.HTTP_201_CREATED:
                return creation_response
            return Response(status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
            return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)  


    @staticmethod
    def handle_get_logs_by_VIN(_vin, user):
        try:
            logs_qs = AssetLogHelper.get_logs_by_vin(_vin, user.db_access).order_by('-asset_log_id')[:300]
            ser = AssetLogSerializer(AssetLogHelper.select_related_to_asset_log(logs_qs), many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_logs_by_VIN_for_daterange(request_data, user):
        try:
            logs_qs = AssetLogHelper.get_logs_by_vin_for_daterange(request_data.get('VIN'), request_data.get('start_date'), request_data.get('end_date'), user.db_access)
            ser = AssetLogSerializer(AssetLogHelper.select_related_to_asset_log(logs_qs), many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def handle_get_event_types(request):
        try:
            choices = AssetLog.event_type_choices
            event_types = [x[1] for x in choices]
            return Response(event_types, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
