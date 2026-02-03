from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_type_checks import AssetTypeChecks
from api.Models.asset_type_checks_history import AssetTypeChecksHistory
from api.Serializers.serializers import AssetTypeChecksHistorySerializer
from api.Models.asset_log import AssetLog
from core.Helper import HelperMethods
from .AssetHistory import AssetHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetTypeChecksHistory():

    @staticmethod
    def create_asset_type_checks_record(asset_type_checks_id, db_name):
        try:
            asset_type_checks = AssetTypeChecks.objects.using(db_name).get(id=asset_type_checks_id)
            asset_type_checks_history_entry, history_response = AssetTypeChecksHistory.generate_asset_type_checks_history_entry(asset_type_checks)
            if history_response.status_code != status.HTTP_200_OK:
                return history_response
            asset_type_checks_history_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_18, e))
            return Response(CustomError.get_full_error_json(CustomError.MHF_18, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_asset_type_checks_record_by_obj(asset_type_checks_obj):
        try:
            asset_type_checks_history_entry, history_response = AssetTypeChecksHistory.generate_asset_type_checks_history_entry(asset_type_checks_obj)
            if history_response.status_code != status.HTTP_200_OK:
                return history_response
            asset_type_checks_history_entry.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_18, e))
            return Response(CustomError.get_full_error_json(CustomError.MHF_18, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def generate_asset_type_checks_history_entry(asset_type_checks_obj):

        asset_type_checks_dict = HelperMethods.django_model_obj_to_dict(asset_type_checks_obj)
        asset_type_checks_dict['asset_type_checks'] = asset_type_checks_obj.id
        ser = AssetTypeChecksHistorySerializer(data=asset_type_checks_dict)

        if ser.is_valid():
            return ser, Response(status=status.HTTP_200_OK)

        Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_18, ser.errors))
        return None, Response(CustomError.get_full_error_json(CustomError.MHF_18, ser.errors), status=status.HTTP_400_BAD_REQUEST)