from os import stat
from rest_framework.response import Response
from rest_framework import status
from core.UserManager.UserHelper import UserHelper
from api.Models.Inventory.inventory import Inventory
from api.Serializers.serializers import InventorySerializer, LightInventorySerializer


import logging
from GSE_Backend.errors.ErrorDictionary import CustomError


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class InventoryHelper:
    @staticmethod
    def mod_inventory_creation_dictionary(requested_data, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        requested_data["created_by"] = detailed_user.detailed_user_id
        requested_data["modified_by"] = detailed_user.detailed_user_id
        return requested_data

    @staticmethod
    def mod_inventory_update_dictionary(requested_data, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        requested_data["modified_by"] = detailed_user.detailed_user_id
        return requested_data

    @staticmethod
    def get_quantity_of_inventory_type(inventory_type:str, user:object) -> int:
        """Get quantity of similar inventory types in the DB

        Args:
            inventory_type (str): Inventory type
            user (object): User object

        Returns:
            int: Quantity of similar inventory types
        """

        return Inventory.objects.using(user.db_access).filter(inventory_type=inventory_type).count()

    @staticmethod
    def select_related_to_inventory(queryset):
        return queryset.select_related("created_by", "modified_by", "location")

    @staticmethod
    def get_all_inventory():
        return Inventory.objects.all()

    @staticmethod
    def get_inventory_by_id(inventory_id):
        try:
            return Inventory.objects.get(id=inventory_id), Response(status=status.HTTP_302_FOUND)
        except Inventory.DoesNotExist as e:
            # inventory id does not exist
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ARDNE_0, e))
            return None, Response(
                CustomError.get_full_error_json(CustomError.ARDNE_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )
