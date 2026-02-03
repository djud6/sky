from rest_framework.response import Response
from rest_framework import status
from ..UserManager.UserHandler import UserHandler
from ..UserManager.UserHelper import UserHelper
from ..UserManager.UserUpdater import UserUpdater
from ..BusinessUnitManager.BusinessUnitHelper import BusinessUnitHelper
from ..RolePermissionsManager.RolePermissionsHelper import RolePermissionsHelper
from ..CompanyManager.CompanyHelper import CompanyHelper
from ..LocationManager.LocationHelper import LocationHelper
from api.Models.DetailedUser import DetailedUser
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class UserImport():

    @staticmethod
    def import_user_csv(parsed_data, user):
        try:
            count = 1
            for user_row in parsed_data:
                count += 1
                if not DetailedUser.objects.using(user.db_access).filter(email=user_row.get("email")).exists():
                    user_row["business_unit"] = BusinessUnitHelper.get_business_unit_id_by_name(user_row.get("business_unit").strip(), user.db_access)
                    user_row["role_permissions"] = RolePermissionsHelper.get_role_permissions_id_by_role(user_row.get("role_permissions"), user.db_access)
                    user_row["company"] = CompanyHelper.get_company_id_by_name(user_row.get("company"), user.db_access)
                    create_user_response = UserHandler.handle_create_user(user_row, user)
                    if create_user_response.status_code != status.HTTP_201_CREATED:
                        return create_user_response
                    print("User row " + str(count) + " email (" + str(user_row.get("email")) + ") has been created")
                else:
                    print("User row " + str(count) + " email (" + str(user_row.get("email")) + ") already exists")

            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_11, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_11, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def import_user_location_csv(parsed_data, db_name):
        try:
            user_location_entries = []
            for user_location_row in parsed_data:
                user_location_row['user_email'] = UserHelper.get_detailed_user_id_by_email(user_location_row.get("user_email"), db_name)
                user_location_row['location_name'] = LocationHelper.get_location_id_by_name(user_location_row.get("location_name"), db_name)
                if not UserHelper.user_location_exists(user_location_row.get("user_email"), user_location_row.get("location_name"), db_name):
                    entry = UserUpdater.create_user_location_entry(user_location_row.get("user_email"), user_location_row.get("location_name"))
                    user_location_entries.append(entry)
            
            UserUpdater.user_location_bulk_create(user_location_entries, db_name)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_11, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_11, e), status=status.HTTP_400_BAD_REQUEST)