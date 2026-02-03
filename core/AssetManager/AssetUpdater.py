from core.Helper import HelperMethods
from core.HistoryManager.AssetHistory import AssetHistory
from rest_framework.response import Response
from rest_framework import status
from ..EquipmentTypeManager.EquipmentTypeHelper import EquipmentTypeHelper
from ..CompanyManager.CompanyHelper import CompanyHelper
from ..LocationManager.LocationHelper import LocationHelper
from ..BusinessUnitManager.BusinessUnitHelper import BusinessUnitHelper
from ..CostCentreManager.CostCentreHelper import CostCentreHelper
from ..CostManager.CostHelper import FuelHelper
from ..UserManager.UserHelper import UserHelper
from ..ManufacturerManager.ManufacturerHelper import ManufacturerHelper
from ..CurrencyManager.CurrencyHelper import CurrencyHelper
from ..JobSpecificationManager.JobSpecificationHelper import JobSpecificationHelper
from .AssetHelper import AssetHelper
from api.Models.asset_model import AssetModel
from api.Models.asset_file import AssetFile
from django.db.models import Q
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
from django.db.models import F
from core.EngineManager.EngineHandler import EngineHandler
from math import ceil

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

        
class AssetUpdater:

    @staticmethod
    def update_usage(VIN, mileage, hours, db_name):
        try:
            asset_obj = AssetModel.objects.using(db_name).get(VIN=VIN)

            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return None, Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            hours_or_mileage = asset_obj.hours_or_mileage.lower()
            daily_average_mileage, daily_average_hours = AssetHelper.calculate_average_daily_usage(VIN, hours_or_mileage, 90, db_name, mileage, hours)
            if hours_or_mileage == AssetModel.Mileage.lower():
                AssetUpdater.update_asset_mileage(VIN=VIN, mileage=mileage, daily_average_mileage=daily_average_mileage, db_name=db_name)
            if hours_or_mileage == AssetModel.Hours.lower():
                AssetUpdater.update_asset_hours(VIN=VIN, hours=hours, daily_average_hours=daily_average_hours, db_name=db_name)
            if hours_or_mileage == AssetModel.Both.lower():
                AssetUpdater.update_asset_mileage_and_hours(VIN=VIN, mileage=mileage, hours=hours, daily_average_mileage=daily_average_mileage, daily_average_hours=daily_average_hours, db_name=db_name)
            if hours_or_mileage == AssetModel.Neither.lower():
                pass
            return asset_obj, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return  None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def update_asset_mileage(VIN, mileage, daily_average_mileage, db_name):
         AssetModel.objects.using(db_name).filter(pk=VIN).update(mileage=mileage, daily_average_mileage=daily_average_mileage)

    @staticmethod
    def update_asset_hours(VIN, hours, daily_average_hours, db_name):
        AssetModel.objects.using(db_name).filter(pk=VIN).update(hours=hours, daily_average_hours=daily_average_hours)

    @staticmethod
    def update_asset_mileage_and_hours(VIN, mileage, hours, daily_average_mileage, daily_average_hours, db_name):
        AssetModel.objects.using(db_name).filter(pk=VIN).update(hours=hours, mileage=mileage, daily_average_mileage=daily_average_mileage, daily_average_hours=daily_average_hours)


    # Updates the status of a given vin
    @staticmethod
    def update_asset_status(_vin, _status):
        asset = AssetModel.objects.filter(pk=_vin).update(status=_status)
        return asset

    # Updates the status of a given asset obj
    # Will be also creating historic record for asset here. Methods that make more updates to asset_obj after this method
    # should not be calling it as they would then need a second historic record.
    @staticmethod
    def update_asset_obj_status_with_history(asset_obj, _status):
        asset_obj.status = _status
        asset_obj.save()
        # Create asset record
        if(not AssetHistory.create_asset_record_by_obj(asset_obj)):
            Logger.getLogger().error(CustomError.MHF_0)
            return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)
        return asset_obj

    #Updates the last process of a given vin
    @staticmethod
    def update_last_process(_vin, _process):
        asset = AssetModel.objects.get(pk=_vin)
        asset.last_process=_process
        asset.date_created = F('date_created')
        asset.save()
        return asset

    #Update asset status for assets in list
    @staticmethod
    def update_status_for_assets_in_list(asset_list, status_update, db_name):
        try:
            AssetModel.objects.using(db_name).filter(VIN__in=asset_list).exclude(status=status_update).update(status=status_update)
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

    # Creates entries and inserts them into db
    @staticmethod
    def create_asset_file_records(asset_obj, file_infos, file_purpose, expiration_date, detailed_user, db_name):
        try:
            entries = list()
            for file_info in file_infos:
                entries.append(AssetUpdater.construct_asset_file_instance(asset_obj, file_info, file_purpose, expiration_date, detailed_user))
            AssetFile.objects.using(db_name).bulk_create(entries)

            return Response(status=status.HTTP_201_CREATED)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0, e))
            return Response(CustomError.get_full_error_json(CustomError.FUF_0, e), status=status.HTTP_400_BAD_REQUEST)


    @staticmethod
    def construct_asset_file_instance(asset_obj, file_info, file_purpose, expiration_date, detailed_user):
        return AssetFile(
            VIN=asset_obj,
            file_type=file_info.file_type,
            file_purpose=file_purpose,
            file_name = file_info.file_name,
            file_url=file_info.file_url,
            bytes=file_info.bytes,
            expiration_date=expiration_date,
            created_by=detailed_user,
            modified_by=detailed_user
        )

    # ----------------------------------------------------------------------------------
   
    @staticmethod 
    def create_asset(request_data, user):
        try:
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            asset, entry_response = AssetUpdater.create_asset_entry(request_data, detailed_user, user.db_access)
            if entry_response.status_code != status.HTTP_201_CREATED:
                return asset, entry_response
            
            asset.save()

            return asset, Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ACF_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ACF_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_asset_entry(request_data, detailed_user, db_name):
        try:
            manufacturer_id = ManufacturerHelper.get_manufacturer_id_by_name(request_data.get("manufacturer"), db_name)
            equipment_type = EquipmentTypeHelper.get_equipment_type_by_model_and_manufacturer(request_data.get('model_number'), manufacturer_id, db_name)
            location = LocationHelper.get_location_by_name(request_data.get('location_name'), db_name)
            business_unit = BusinessUnitHelper.get_business_unit_by_name_and_location(request_data.get('business_unit_name'), request_data.get('location_name'), db_name)
            job_specification, response = JobSpecificationHelper.get_job_specification_by_name(request_data.get("job_specification"), db_name)
            company, response = CompanyHelper.get_company_by_name(request_data.get('company'), db_name)
            return AssetModel(
                VIN=request_data.get('VIN'),
                equipment_type=equipment_type,
                company=company,
                original_location=location,
                current_location=location,
                department=business_unit,
                job_specification=job_specification,
                created_by=detailed_user,
                modified_by=detailed_user
            ), Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ACF_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ACF_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

    @staticmethod
    def update_asset_fields(asset_entry, request_data, user):
        try:
            # Check if asset status is inactive
            if not AssetHelper.check_asset_status_active(asset_entry.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Update required fields
            updated_asset, update_required_response = AssetUpdater.update_asset_required_fields(asset_entry, request_data, user.db_access)
            if update_required_response.status_code != status.HTTP_200_OK:
                return updated_asset, update_required_response

            # Update optional fields
            updated_asset, update_optional_response = AssetUpdater.update_asset_optional_fields(asset_entry, request_data, user)
            if update_optional_response.status_code != status.HTTP_200_OK:
                return updated_asset, update_optional_response

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            updated_asset.modified_by = detailed_user
            updated_asset.save()

            return updated_asset, Response(status=status.HTTP_202_ACCEPTED)
            
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_2, e))
            return asset_entry, Response(CustomError.get_full_error_json(CustomError.TUF_2, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------
    
    @staticmethod
    def update_asset_required_fields(asset_entry, request_data, db_name):
        try:
            if not len(str(request_data.get("job_specification"))) == 0 and request_data.get("job_specification") is not None:
                job_specification, job_spec_response = JobSpecificationHelper.get_job_specification_by_id(request_data.get("job_specification"), db_name)
                if job_spec_response.status_code != status.HTTP_302_FOUND:
                    return asset_entry, job_spec_response
                asset_entry.job_specification = job_specification

            if not len(str(request_data.get("business_unit"))) == 0 and request_data.get("business_unit") is not None:
                business_unit, business_unit_spec_response = BusinessUnitHelper.get_business_unit_by_id(request_data.get("business_unit"), db_name)
                if business_unit_spec_response.status_code != status.HTTP_302_FOUND:
                    return asset_entry, business_unit_spec_response
                asset_entry.department = business_unit

            return asset_entry, Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_2, e))
            return asset_entry, Response(CustomError.get_full_error_json(CustomError.TUF_2, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

    @staticmethod
    def update_asset_optional_fields(asset_entry, request_data, user):
        try:
            # Check if asset status is inactive
            if not AssetHelper.check_asset_status_active(asset_entry.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            db_name = user.db_access
            if not len(str(request_data.get("parent_VIN"))) == 0 and request_data.get("parent_VIN") is not None:
                if str(request_data.get("parent_VIN")).lower() == "none":
                    asset_entry.parent = None
                else:
                    asset_entry.parent = AssetHelper.get_asset_by_VIN(request_data.get("parent_VIN"), db_name)

            if not len(str(request_data.get("jde_department"))) == 0 and request_data.get("jde_department") is not None:
                asset_entry.jde_department = request_data.get("jde_department").strip()

            if not len(str(request_data.get("status"))) == 0 and request_data.get("status") is not None:
                asset_entry.status = request_data.get("status").strip()

            if not len(str(request_data.get("aircraft_compatability"))) == 0 and request_data.get("aircraft_compatability") is not None:
                asset_entry.aircraft_compatability = request_data.get("aircraft_compatability").strip()

            if not len(str(request_data.get("unit_number"))) == 0 and request_data.get("unit_number") is not None:
                asset_entry.unit_number = request_data.get("unit_number").strip()

            if not len(str(request_data.get("license_plate"))) == 0 and request_data.get("license_plate") is not None:
                asset_entry.license_plate = request_data.get("license_plate").strip()

            if not len(str(request_data.get("date_of_manufacture"))) == 0 and request_data.get("date_of_manufacture") is not None:
                asset_entry.date_of_manufacture = request_data.get("date_of_manufacture").strip()

            if not len(str(request_data.get("fire_extinguisher_quantity"))) == 0 and request_data.get("fire_extinguisher_quantity") is not None:
                asset_entry.fire_extinguisher_quantity = request_data.get("fire_extinguisher_quantity").strip()

            if not len(str(request_data.get("fire_extinguisher_inspection_date"))) == 0 and request_data.get("fire_extinguisher_inspection_date") is not None:
                asset_entry.fire_extinguisher_inspection_date = request_data.get("fire_extinguisher_inspection_date").strip()

            if not len(str(request_data.get("path"))) == 0 and request_data.get("path") is not None:
                asset_entry.path = request_data.get("path").strip()

            if not len(str(request_data.get("last_process"))) == 0 and request_data.get("last_process") is not None:
                asset_entry.last_process = request_data.get("last_process").strip()

            if not len(str(request_data.get("mileage"))) == 0 and request_data.get("mileage") is not None:
                asset_entry.mileage = request_data.get("mileage").strip().replace(",", "")
            # remove later
            asset_entry.mileage = 1000

            if not len(str(request_data.get("hours"))) == 0 and request_data.get("hours") is not None:
                asset_entry.hours = request_data.get("hours").strip().replace(",", "")

            if not len(str(request_data.get("mileage_unit"))) == 0 and request_data.get("mileage_unit") is not None:
                asset_entry.mileage_unit = request_data.get("mileage_unit").strip()

            if not len(str(request_data.get("date_in_service"))) == 0 and request_data.get("date_in_service") is not None:
                asset_entry.date_in_service = request_data.get("date_in_service").strip()
            # remove later
            asset_entry.date_in_service = "2015-03-08"

            if not len(str(request_data.get("currency"))) == 0 and request_data.get("currency") is not None:
                asset_entry.currency = CurrencyHelper.get_currency_by_code(request_data.get("currency").strip(), db_name)

            if not len(str(request_data.get("replacement_hours"))) == 0 and request_data.get("replacement_hours") is not None:
                asset_entry.replacement_hours = request_data.get("replacement_hours").strip().replace(",", "")

            if not len(str(request_data.get("replacement_mileage"))) == 0 and request_data.get("replacement_mileage") is not None:
                asset_entry.replacement_mileage = request_data.get("replacement_mileage").strip().replace(",", "")

            if not len(str(request_data.get("insurance_renewal_date"))) == 0 and request_data.get("insurance_renewal_date") is not None:
                asset_entry.insurance_renewal_date = request_data.get("insurance_renewal_date").strip()

            if not len(str(request_data.get("registration_renewal_date"))) == 0 and request_data.get("registration_renewal_date") is not None:
                asset_entry.registration_renewal_date = request_data.get("registration_renewal_date").strip()

            if not len(str(request_data.get("load_capacity"))) == 0 and request_data.get("load_capacity") is not None:
                asset_entry.load_capacity = request_data.get("load_capacity").strip().replace(",", "")

            if not len(str(request_data.get("load_capacity_unit"))) == 0 and request_data.get("load_capacity_unit") is not None:
                asset_entry.load_capacity_unit = request_data.get("load_capacity_unit").strip()

            if not len(str(request_data.get("engine"))) == 0 and request_data.get("engine") is not None:
                asset_entry.engine = request_data.get("engine").strip()

            if not len(str(request_data.get("fuel"))) == 0 and request_data.get("fuel") is not None:
                fuel_entry, asset_entry_response = FuelHelper.get_fuel_type_by_name(request_data.get("fuel"), db_name)
                if asset_entry_response.status_code == status.HTTP_302_FOUND:
                    asset_entry.fuel = fuel_entry

            if not len(str(request_data.get("hours_or_mileage"))) == 0 and request_data.get("hours_or_mileage") is not None:
                asset_entry.hours_or_mileage = request_data.get("hours_or_mileage")
            #remove later
            asset_entry.hours_or_mileage = "mileage"

            if not len(str(request_data.get("fuel_tank_capacity"))) == 0 and request_data.get("fuel_tank_capacity") is not None:
                asset_entry.fuel_tank_capacity = request_data.get("fuel_tank_capacity")

            if not len(str(request_data.get("fuel_tank_capacity_unit"))) == 0 and request_data.get("fuel_tank_capacity_unit") is not None:
                asset_entry.fuel_tank_capacity_unit = request_data.get("fuel_tank_capacity_unit").strip()

            if not len(str(request_data.get("is_rental"))) == 0 and request_data.get("is_rental") is not None:
                asset_entry.is_rental = HelperMethods.validate_bool(request_data.get("is_rental"))

            if not len(str(request_data.get("monthly_subscription_cost"))) == 0 and request_data.get("monthly_subscription_cost") is not None:
                asset_entry.monthly_subscription_cost = request_data.get("monthly_subscription_cost")

            if not len(str(request_data.get("class_code"))) == 0 and request_data.get("class_code") is not None:
                asset_entry.class_code = request_data.get("class_code").strip()
        
            if not len(str(request_data.get("asset_description"))) == 0 and request_data.get("asset_description") is not None:
                asset_entry.asset_description = request_data.get("asset_description").strip()
               
            if not len(str(request_data.get("custom_fields"))) == 0 and request_data.get("custom_fields") is not None:
                asset_entry.custom_fields = request_data.get("custom_fields").strip()
            
            if request_data.get("cost_centre_name")!=None:
                cost_centre,cost_centre_response=CostCentreHelper.get_by_name(db_name,request_data.get("cost_centre_name"))
                if cost_centre_response.status_code!=status.HTTP_302_FOUND:
                    return asset_entry,cost_centre_response
                asset_entry.cost_centre=cost_centre
            
            if request_data.get("cost_centre")!=None:
                cost_centre,cost_centre_response=CostCentreHelper.get_by_id(db_name,request_data.get("cost_centre"))
                if cost_centre_response.status_code!=status.HTTP_302_FOUND:
                    return asset_entry,cost_centre_response
                asset_entry.cost_centre=cost_centre
            
            engines=request_data.get("engines")
            if engines:
                response=EngineHandler.handle_update_multiple(user,engines,None,True,asset_entry)
                if response.status_code!=status.HTTP_200_OK:
                    return None,response
            
            lifespan_years=request_data.get("lifespan_years")
            if lifespan_years!=None:
                lifespan_years_value=ceil(float(lifespan_years))
                if not lifespan_years_value>=1:
                    return None,Response(CustomError.AUHF_2,status.HTTP_400_BAD_REQUEST)
                asset_entry.lifespan_years=lifespan_years_value

            return asset_entry, Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_2, e))
            return asset_entry, Response(CustomError.get_full_error_json(CustomError.TUF_2, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

    @staticmethod
    def update_asset_total_cost(delte_cost, asset_obj):
        try:
            asset_obj.total_cost += delte_cost
            asset_obj.date_created = F('date_created')
            return asset_obj, Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_2, e))
            return asset_obj, Response(CustomError.get_full_error_json(CustomError.TUF_2, e), status=status.HTTP_400_BAD_REQUEST)  
