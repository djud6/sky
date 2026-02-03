from core.InspectionTypeManager.InspectionTypeHelper import InspectionTypeHelper
from core.MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from core.AssetManager.AssetHelper import AssetHelper
from core.LocationManager.LocationHelper import LocationHelper
from rest_framework.response import Response
from rest_framework import status
from ..MaintenanceManager.MaintenanceUpdater import MaintenanceUpdater
from ..UserManager.UserHelper import UserHelper
from ..HistoryManager.MaintenanceHistory import MaintenanceHistory
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.maintenance_request_history import MaintenanceRequestModelHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceImport():

    @staticmethod
    def import_maintenance_csv(parsed_data, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            maintenance_entries = []
            count = 0
            for maintenance_row in parsed_data:
                count += 1
                try:
                    if MaintenanceHelper.does_maintenance_entry_exist_by_other(maintenance_row, user.db_access):
                        print("Row " + str(count) + ": This maintenance entry already appears to exist.")
                        continue
                    else:
                        
                        if not AssetHelper.asset_exists(maintenance_row.get("VIN"), user.db_access):
                            print("Row " + str(count) + ": Provided VIN does not exist in the database.")
                            continue
                        if not InspectionTypeHelper.inspection_type_exists_by_code(maintenance_row.get("inspection_code"), user.db_access):
                            print("Row " + str(count) + ": Provided inspection code does not exist in the database.")
                            continue
                        if not LocationHelper.location_exists_by_name(maintenance_row.get("location_name"), user.db_access):
                            print("Row " + str(count) + ": Provided location does not exist in the database.")
                            continue

                        entry = MaintenanceUpdater.create_maintenance_entry(maintenance_row, detailed_user, user.db_access)
                        maintenance_entries.append(entry)
                        print("Row " + str(count) + ": Added maintenance entry.")

                except Exception as e:
                    print("Row " + str(count) + " Error: " + str(e))

            MaintenanceRequestModel.objects.using(user.db_access).bulk_create(maintenance_entries)

            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_16, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_16, e), status=status.HTTP_400_BAD_REQUEST)


                                                        

