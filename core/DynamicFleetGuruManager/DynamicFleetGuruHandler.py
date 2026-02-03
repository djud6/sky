from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_model import AssetModel
from core.AssetManager.AssetHelper import AssetHelper
from core.UserManager.UserHelper import UserHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DynamicFleetGuruHandler():

    @staticmethod
    def handle_underused_assets(user):
        try:
            asset_by_hours = AssetHelper.filter_assets_for_user(AssetHelper.get_all_assets(user.db_access).filter(hours_or_mileage=AssetModel.Hours).order_by('daily_average_hours'), user).values('VIN', 'hours_or_mileage', 'daily_average_mileage', 'daily_average_hours', 'equipment_type__asset_type__name')
            asset_by_mileage = AssetHelper.filter_assets_for_user(AssetHelper.get_all_assets(user.db_access).filter(hours_or_mileage=AssetModel.Mileage).order_by('daily_average_mileage'), user).values('VIN', 'hours_or_mileage', 'daily_average_mileage', 'daily_average_hours', 'equipment_type__asset_type__name')
            asset_by_both = AssetHelper.filter_assets_for_user(AssetHelper.get_all_assets(user.db_access).filter(hours_or_mileage=AssetModel.Both).order_by('daily_average_mileage', 'daily_average_hours'), user).values('VIN', 'hours_or_mileage', 'daily_average_mileage', 'daily_average_hours', 'equipment_type__asset_type__name')
            
            underused_assets = {'hours': None,
                                'mileage': None,
                                'both': None}

            underused_by_types = DynamicFleetGuruHandler.set_key_for_underused_type(asset_by_hours, {})
            underused_assets['hours'] = underused_by_types
            underused_by_types = DynamicFleetGuruHandler.set_key_for_underused_type(asset_by_mileage, {})
            underused_assets['mileage'] = underused_by_types
            underused_by_types = DynamicFleetGuruHandler.set_key_for_underused_type(asset_by_both, {})
            underused_assets['both'] = underused_by_types

            suggestion = "If an asset is being underutilized it may not be useful in its current location and is costing you money in storage and depreciation. "\
            "Transfering it to a location where it is needed or outright selling the asset may be the best course of action for your fleet."

            return Response({'suggestion': suggestion, 'data': underused_assets}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def set_key_for_underused_type(assets, underused_by_types):
        for asset in assets:
            if asset.get('equipment_type__asset_type__name') in dict.keys(underused_by_types):
                underused_by_types[asset.get('equipment_type__asset_type__name')].append(asset)
            else:
                underused_by_types[asset.get('equipment_type__asset_type__name')] = []
        return underused_by_types
        
# ---------------------------------------------------------------------------------------------------------------------
    