from rest_framework.response import Response
from rest_framework import status

from core.AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from ..AssetTypeManager.AssetTypeHelper import AssetTypeHelper
from api.Models.asset_type_checks import AssetTypeChecks
from api.Serializers.serializers import AssetTypeChecksSerializer, AssetTypeSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)




class AssetTypeHandler():

    @staticmethod
    def handle_get_asset_types_with_checks(user):
        try:
            asset_types = AssetTypeHelper.get_asset_types_with_checks(user.db_access)
            ser = AssetTypeSerializer(asset_types, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_asset_types_without_checks(user):
        try:
            asset_types = AssetTypeHelper.get_asset_types_without_checks(user.db_access)
            ser = AssetTypeSerializer(asset_types, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_asset_type_checks(request_data, user):
        try:
            # check if asset type exists
            if not AssetTypeHelper.asset_type_exists_by_name(request_data.get('asset_type_name'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.ATNDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.ATNDNE_0), status=status.HTTP_400_BAD_REQUEST)

            # add checks for asset type
            ser = AssetTypeChecksSerializer(data=request_data)
            if ser.is_valid():
                ser.save()
                return Response(status=status.HTTP_200_OK)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_asset_type_checks(user):
        try:
            checks = AssetTypeChecksHelper.get_all_asset_type_checks(user.db_access)
            ser = AssetTypeChecksSerializer(checks, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


