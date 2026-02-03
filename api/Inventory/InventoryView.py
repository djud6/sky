from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.InventoryManager.InventoryHandler import InventoryHandler


class AddInventory(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return InventoryHandler.handle_add_inventory(request.data, request.user)


class UpdateInventory(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return InventoryHandler.handle_update_inventory(request.data, request.user)


class ListInventory(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return InventoryHandler.handle_list_inventory()


class GetInventoryByID(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, inventory_id):
        return InventoryHandler.handle_get_inventory_by_id(inventory_id)
