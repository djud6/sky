from rest_framework.response import Response
from rest_framework import status
from api.Models.user_configuration import UserConfiguration
from api_auth.Auth_User.User import User
from rest_framework import status
from api.Models.DetailedUser import DetailedUser
from api.Models.business_unit import BusinessUnitModel
from api.Models.Company import Company
from api.Models.RolePermissions import RolePermissions
from api.Models.locations import LocationModel
import re
import string
import random
from datetime import datetime
from GSE_Backend.errors.ErrorDictionary import CustomError

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class UserHelper:

    auth_db_name = "auth_db"

    @staticmethod
    def user_location_exists(user_id, location_id, db_name):
        return DetailedUser.location.through.objects.using(db_name).filter(detaileduser_id=user_id, locationmodel_id=location_id).exists()

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return status.HTTP_404_NOT_FOUND


    @staticmethod
    def get_user_by_email(user_email):
        try:
            return User.objects.get(email=user_email)
        except:
            return status.HTTP_404_NOT_FOUND

    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            Logger.getLogger().error(CustomError.IP_0)
            return Response(CustomError.get_full_error_json(CustomError.IP_0), status=status.HTTP_400_BAD_REQUEST)
        elif re.search('[0-9]',password) is None:
            Logger.getLogger().error(CustomError.IP_1)
            return Response(CustomError.get_full_error_json(CustomError.IP_1), status=status.HTTP_400_BAD_REQUEST)
        elif re.search('[A-Z]',password) is None:
            Logger.getLogger().error(CustomError.IP_2)
            return Response(CustomError.get_full_error_json(CustomError.IP_2), status=status.HTTP_400_BAD_REQUEST) 
        elif len(password) > 32:
            Logger.getLogger().error(CustomError.IP_3)
            return Response(CustomError.get_full_error_json(CustomError.IP_3), status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response(status=status.HTTP_200_OK)

    @staticmethod
    def generate_random_password(size=9, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size)) + str(datetime.utcnow().year)

    # Get model instances

    @staticmethod
    def get_user_obj(_id):
        return User.objects.using(UserHelper.auth_db_name).get(pk=_id)

    @staticmethod
    def get_all_users_for_company(db_name):
        return User.objects.using("auth_db").filter(db_access=db_name)

    @staticmethod
    def get_all_active_users_for_company(db_name):
        return User.objects.using("auth_db").filter(db_access=db_name, is_active=True)

    @staticmethod
    def get_user_obj_by_email(email):
        return User.objects.using(UserHelper.auth_db_name).get(email=email)

    @staticmethod
    def get_detailed_user_obj(email, db_name):
        return DetailedUser.objects.using(db_name).get(email=email)
    
    @staticmethod
    def get_detailed_users_by_emails(emails, db_name):
        return DetailedUser.objects.using(db_name).filter(email__in=emails)

    @staticmethod
    def get_detailed_user_id_by_email(email, db_name):
        return DetailedUser.objects.using(db_name).filter(email=email).values_list('detailed_user_id', flat=True)[0]

    @staticmethod
    def get_business_unit_obj(_id, db_name):
        return BusinessUnitModel.objects.using(db_name).get(pk=_id)

    @staticmethod
    def get_company_obj_by_id(_id, db_name):
        return Company.objects.using(db_name).get(pk=_id)

    @staticmethod
    def get_company_obj_by_user_email(email, db_name):
        return DetailedUser.objects.using(db_name).get(email=email).company

    @staticmethod
    def get_company_name_by_user_email(email, db_name):
        return DetailedUser.objects.using(db_name).get(email=email).company.company_name

    @staticmethod
    def get_role_permissions_obj(_id, db_name):
        return RolePermissions.objects.using(db_name).get(pk=_id)

    @staticmethod
    def get_all_operators(db_name):
        return DetailedUser.objects.using(db_name).filter(role_permissions__role=RolePermissions.operator)

    @staticmethod
    def get_all_managers(db_name):
        return DetailedUser.objects.using(db_name).filter(role_permissions__role=RolePermissions.manager)

    @staticmethod
    def get_all_supervisors(db_name):
        return DetailedUser.objects.using(db_name).filter(role_permissions__role=RolePermissions.supervisor)

    @staticmethod
    def get_user_location_table(db_name):
        return DetailedUser.location.through.objects.using(db_name).all()

    @staticmethod
    def get_role_by_email(email, db_name):
        return DetailedUser.objects.using(db_name).get(email=email).role_permissions.role

    @staticmethod
    def get_user_config_by_user_id(detailed_user_id, db_name):
        try:
            return UserConfiguration.objects.using(db_name).get(user_id=detailed_user_id)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.UDNE_1, e))
            return None, Response(CustomError.get_full_error_json(CustomError.UDNE_1, e), status=status.HTTP_400_BAD_REQUEST)

    # Check if entries exist for the provided id

    @staticmethod
    def id_user_entry_exists(user_id):
        return User.objects.using(UserHelper.auth_db_name).filter(pk=user_id).exists()

    @staticmethod
    def email_user_entry_exists(email):
        try:
            return User.objects.using(UserHelper.auth_db_name).filter(email=email).exists()
        except:
            return status.HTTP_404_NOT_FOUND
    @staticmethod
    def business_unit_entry_exists(_id, db_name):
        return BusinessUnitModel.objects.using(db_name).filter(pk=_id).exists()

    @staticmethod
    def company_entry_exists(_id, db_name):
        return Company.objects.using(db_name).filter(pk=_id).exists()

    @staticmethod
    def role_permissions_entry_exists(_id, db_name):
        return RolePermissions.objects.using(db_name).filter(pk=_id).exists()

    @staticmethod
    def user_foreign_keys_exist(request_data, user):
        if not len(str(request_data.get("business_unit"))) == 0 and request_data.get("business_unit") is not None:
            # Does business_unit entry exist
            if(not UserHelper.business_unit_entry_exists(request_data.get("business_unit"), user.db_access)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.BUDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.BUDNE_0), status=status.HTTP_400_BAD_REQUEST)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.I_1))
            return Response(CustomError.get_full_error_json(CustomError.I_1), status=status.HTTP_400_BAD_REQUEST)

        if not len(str(request_data.get("role_permissions"))) == 0 and request_data.get("role_permissions") is not None:
            # Does role_permissions entry exist
            if(not UserHelper.role_permissions_entry_exists(request_data.get("role_permissions"), user.db_access)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.RPDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.RPDNE_0), status=status.HTTP_400_BAD_REQUEST)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.I_1))
            return Response(CustomError.get_full_error_json(CustomError.I_1), status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_user_locations_by_email(user_email, db_name):
        detailed_user = UserHelper.get_detailed_user_obj(user_email, db_name)
        return detailed_user.location.values_list('location_id', flat=True)

    @staticmethod
    def get_user_locations_by_user_obj(detailed_user):
        return detailed_user.location.values_list('location_id', flat=True)

    @staticmethod
    def delete_locations_by_user_detailed_user_id(user_id, db_name):
        return DetailedUser.location.through.objects.using(db_name).filter(detaileduser_id=user_id).delete()

    @staticmethod
    def location_id_exists(location_id, db_name):
        return LocationModel.objects.using(db_name).filter(location_id=location_id).exists()

    @staticmethod
    def get_managers_emails_by_location(db_name, locations):
        return DetailedUser.objects.using(db_name).filter(role_permissions__role='manager', location__in=locations).values_list('email', flat=True).distinct()
    
    @staticmethod
    def get_detailed_users_by_ids(user_ids, db_name):
        return DetailedUser.objects.using(db_name).filter(detailed_user_id__in=user_ids)

    @staticmethod
    def get_detailed_users_by_location_ids(location_ids, db_name):
        return DetailedUser.objects.using(db_name).filter(location__location_id__in=location_ids)
    
    @staticmethod
    def get_detailed_users_by_business_unit_ids(business_unit_ids, db_name):
        return DetailedUser.objects.using(db_name).filter(business_unit__in=business_unit_ids)
    
    @staticmethod
    def get_detailed_users_by_role_ids(role_ids, db_name):
        return DetailedUser.objects.using(db_name).filter(role_permissions__in=role_ids)
    
