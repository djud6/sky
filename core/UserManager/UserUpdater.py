from rest_framework.response import Response
from rest_framework import status
from ..Helper import HelperMethods
from .UserHelper import UserHelper
from api.Models.DetailedUser import DetailedUser
from api.Models.user_configuration import UserConfiguration
from django.utils import timezone
from GSE_Backend.errors.ErrorDictionary import CustomError
from core.CostCentreManager.CostCentreHelper import CostCentreHelper
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class UserUpdater():

    @staticmethod
    def update_user_password(user_obj, password):
        user_obj.set_password(password)
        user_obj.save()
        return user_obj

    @staticmethod
    def update_user_last_login(user_obj):
        user_obj.last_login = timezone.now()
        user_obj.save()
        return user_obj

    @staticmethod
    def update_user_account(user_obj, detailed_user_obj, request_data, db_name):
        try:
            if not len(str(request_data.get("email"))) == 0 and request_data.get("email") is not None:
                user_obj.email = str(request_data.get("email"))
                user_obj.username = user_obj.email
                detailed_user_obj.email = str(request_data.get("email"))
            
            if not len(str(request_data.get("first_name"))) == 0 and request_data.get("first_name") is not None:
                user_obj.first_name = str(request_data.get("first_name"))

            if not len(str(request_data.get("last_name"))) == 0  and request_data.get("last_name") is not None:
                user_obj.last_name = str(request_data.get("last_name"))

            if not len(str(request_data.get("is_superuser"))) == 0 and request_data.get("is_superuser") is not None:
                user_obj.is_superuser = HelperMethods.validate_bool(request_data.get("is_superuser"))

            if not len(str(request_data.get("is_staff"))) == 0 and request_data.get("is_staff") is not None:
                user_obj.is_staff = HelperMethods.validate_bool(request_data.get("is_staff"))

            if not len(str(request_data.get("is_active"))) == 0 and request_data.get("is_active") is not None:
                user_obj.is_active = HelperMethods.validate_bool(request_data.get("is_active"))

            if not len(str(request_data.get("cost_allowance"))) == 0 and request_data.get("cost_allowance") is not None:
                detailed_user_obj.cost_allowance = request_data.get("cost_allowance")

            if not len(str(request_data.get("company"))) == 0 and request_data.get("company") is not None:
                detailed_user_obj.company = UserHelper.get_company_obj_by_id(request_data.get("company"), db_name)

            if not len(str(request_data.get("role_permissions"))) == 0 and request_data.get("role_permissions") is not None:
                detailed_user_obj.role_permissions = UserHelper.get_role_permissions_obj(request_data.get("role_permissions"), db_name)

            if not len(str(request_data.get("business_unit"))) == 0 and request_data.get("business_unit") is not None:
                detailed_user_obj.business_unit = UserHelper.get_business_unit_obj(request_data.get("business_unit"), db_name)

            if not len(str(request_data.get("agreement_accepted"))) == 0 and request_data.get("agreement_accepted") is not None:
                detailed_user_obj.agreement_accepted = HelperMethods.validate_bool(request_data.get("agreement_accepted"))
            
            if not len(str(request_data.get("cost_centre"))) == 0 and request_data.get("cost_centre") is not None:
                detailed_user_obj.cost_centre, _ = CostCentreHelper.get_by_id(db_name,request_data.get("cost_centre"))

            user_obj.save()
            detailed_user_obj.save()
            return user_obj, detailed_user_obj, ""

        except Exception as e:
            Logger.getLogger().error(e)
            return None, None, str(e)


    @staticmethod
    def user_location_bulk_create(entries, db_name):
        DetailedUser.location.through.objects.using(db_name).bulk_create(entries)


    @staticmethod
    def create_detailed_user(request_data, user_email, db_name):
        try:
            detailed_user_entry = UserUpdater.create_detailed_user_entry(request_data, user_email, db_name)
            detailed_user_entry.save()
            return detailed_user_entry, Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def create_detailed_user_entry(request_data, user_email, db_name):
        cost_centre, _ = CostCentreHelper.get_by_id(db_name,request_data.get("cost_centre"))
        return DetailedUser(
            email = request_data.get("email"),
            business_unit = UserHelper.get_business_unit_obj(request_data.get("business_unit"), db_name),
            company = UserHelper.get_company_obj_by_user_email(user_email, db_name),
            role_permissions = UserHelper.get_role_permissions_obj(request_data.get("role_permissions"), db_name),
            cost_allowance = request_data.get("cost_allowance"),
            cost_centre = cost_centre
        )


    @staticmethod
    def create_user_location_entry(detaileduser_id, locationmodel_id):
        return DetailedUser.location.through(
            detaileduser_id=detaileduser_id,
            locationmodel_id=locationmodel_id
        )
    

    @staticmethod
    def delete_user_location_entry(detaileduser_id):
        return DetailedUser.location.through(
            detaileduser_id=detaileduser_id
        ).delete()


    @staticmethod
    def update_user_permission(user, permission):
        if user.is_superuser:
            DetailedUser.objects.using(user.db_access).filter(email=user.email).update(role_permissions=permission)
            return Response(status=status.HTTP_200_OK)

    @staticmethod
    def create_user_configuration(detailed_user):
        try:
            detailed_config_entry = UserUpdater.create_user_configuration_entry(detailed_user)
            detailed_config_entry.save()
            return detailed_config_entry, Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_user_configuration_entry(detailed_user):
        return UserConfiguration(user=detailed_user)

    @staticmethod
    def update_user_config(config_obj, request_data):
        try:
            sound = request_data.get("sound")
            if sound is not None and len(str(sound)) > 0:
                config_obj.sound = str(sound)

            sound_percentage = request_data.get("sound_percentage")
            if sound_percentage is not None and len(str(sound_percentage)) > 0:
                config_obj.sound_percentage = str(sound_percentage)

            dashboard_layout = request_data.get("dashboard_layout")
            if dashboard_layout is not None and len(str(dashboard_layout)) > 0:
                config_obj.dashboard_layout = str(dashboard_layout)

            table_filter = request_data.get("table_filter")
            if table_filter is not None and len(str(table_filter)) > 0:
                config_obj.table_filter = str(table_filter)

            config_obj.save()
            return config_obj, ""

        except Exception as e:
            Logger.getLogger().error(e)
            return None, str(e)
