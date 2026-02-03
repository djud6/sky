from rest_framework.response import Response
from rest_framework import status
from api.Models.Inventory.inventory import Inventory
from api.Serializers.serializers import InventorySerializer, LightInventorySerializer
from core.InventoryManager.InventoryHelper import InventoryHelper

import logging
from GSE_Backend.errors.ErrorDictionary import CustomError


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class InventoryHandler:
    @staticmethod
    def handle_add_inventory(requested_data, user):
        try:
            requested_data = InventoryHelper.mod_inventory_creation_dictionary(
                requested_data, user
            )
            ser = InventorySerializer(data=requested_data)
            if ser.is_valid():
                inventory_obj = ser.save()
                return Response({"inventory_id": inventory_obj.id}, status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(
                    CustomError.get_full_error_json(
                        CustomError.S_0, ser.errors),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def handle_update_inventory(requested_data, user):
        try:
            inventory_id = requested_data.get("inventory_id")
            update_data = InventoryHelper.mod_inventory_update_dictionary(
                requested_data.get("update_data"), user
            )
            Inventory.objects.filter(id=inventory_id).update(**update_data)
            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def handle_list_inventory():
        try:
            all_inventory = InventoryHelper.select_related_to_inventory(
                InventoryHelper.get_all_inventory()
            )
            ser = LightInventorySerializer(all_inventory, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def handle_get_inventory_by_id(inventory_id):
        try:
            inventory_entry, inventory_response = InventoryHelper.get_inventory_by_id(
                inventory_id)
            if inventory_response.status_code != status.HTTP_302_FOUND:
                return inventory_response
            ser = LightInventorySerializer(inventory_entry)
            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(
                CustomError.get_full_error_json(CustomError.G_0, e),
                status=status.HTTP_400_BAD_REQUEST,
            )
