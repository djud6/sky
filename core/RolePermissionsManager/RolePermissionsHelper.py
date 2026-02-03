from rest_framework.response import Response
from rest_framework import status
from api.Models.RolePermissions import RolePermissions
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RolePermissionsHelper():

    @staticmethod
    def get_all_role_permissions(db_name):
        return RolePermissions.objects.using(db_name).all()

    @staticmethod
    def get_role_permissions_id_by_role(role, db_name):
        return RolePermissions.objects.using(db_name).filter(role=role).values_list('id', flat=True)[0]