from rest_framework.response import Response
from rest_framework import status
from ..RolePermissionsManager.RolePermissionsUpdater import RolePermissionsUpdater
from api.Models.RolePermissions import RolePermissions
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RolePermissionsImport():

    @staticmethod
    def import_role_permissions_csv(parsed_data, db_name):
        try:
            role_permissions_entries = []
            for role_permissions_row in parsed_data:
                if not RolePermissions.objects.using(db_name).filter(role=role_permissions_row.get("role")).exists():
                    entry = RolePermissionsUpdater.create_role_permissions_entry(role_permissions_row)
                    role_permissions_entries.append(entry)
            RolePermissions.objects.using(db_name).bulk_create(role_permissions_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_7, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_7, e), status=status.HTTP_400_BAD_REQUEST)