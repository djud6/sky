from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_model import AssetModel
from api.Models.asset_model_history import AssetModelHistory
from api.Models.asset_file import AssetFile
from api.Models.DetailedUser import DetailedUser
from api.Models.RolePermissions import RolePermissions
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from core.FileManager.FileInfo import FileInfo
from ..UserManager.UserHelper import UserHelper
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from ..Helper import HelperMethods
from datetime import datetime
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
from api.Models.engine import EngineModel

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetHelper:

    @staticmethod
    def select_related_to_asset(queryset):
        return queryset.select_related('equipment_type', 'equipment_type__manufacturer', 'equipment_type__asset_type', 'department', 'original_location', 'current_location', 'fuel', 'company')
    
    @staticmethod
    def get_serializer_context_2(assets,user):
      
        # TODO: moved here to avoid cyclic import, but ugly...
        
        from ..DisposalManager.DisposalHelper import DisposalHelper
        from ..TransferManager.TransferHelper import TransferHelper
      
        disposals=DisposalHelper.get_latest_asset_disposals(user.db_access)
        transfers=TransferHelper.get_latest_asset_transfer(user.db_access)
        context=AssetHelper.filter_asset_query({
            "disposal":disposals,
            "transfer":transfers,
        })
        
        # TODO: weird
        
        if not assets:
            assets=AssetHelper.get_all_assets(user.db_access)
        
        context["asset_parent_dict_list"]=list(assets.exclude(parent=None).values("VIN","parent"))

        context["engines"] = AssetHelper.get_all_engines(user.db_access).values()

        all_asset_expiration_dates = AssetHelper.get_all_asset_expiration_dates(user.db_access,
                                                                                assets.values_list("VIN", flat=True))
        context["expiration_dates"] = AssetHelper.filter_asset_expiration_date(all_asset_expiration_dates)
        return context

    # ----------------------------------------------------------------------------------------------

    # This method will take an asset qs and filter it to only show assets relevant to user
    @staticmethod
    def filter_assets_for_user(asset_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        if(detailed_user.role_permissions.role == RolePermissions.executive or detailed_user.role_permissions.role == RolePermissions.manager):
            return asset_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return asset_qs.filter(current_location__in=user_locations)

    @staticmethod
    def asset_for_user(asset, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if (detailed_user.role_permissions.role == RolePermissions.executive
                or detailed_user.role_permissions.role == RolePermissions.manager):
            return True

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        if (asset.current_location in user_locations.location_id
                or asset.original_location.location_id in user_locations):
            return True
        
        return False

    # This method will take an asset qs and filter it to only show assets that are currently in one of the user's locations.
    @staticmethod
    def filter_assets_for_daily_checks_for_user(asset_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return asset_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return asset_qs.filter(current_location__in=user_locations)    

    # This method will take an asset qs and filter it to only show assets that are currently in one of the user's locations.
    @staticmethod
    def filter_assets_for_maintenance_for_user(asset_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return asset_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return asset_qs.filter(current_location__in=user_locations)

    # ----------------------------------------------------------------------------------------------
    
    @staticmethod
    def validate_usage_update(asset_obj, mileage, hours, db_name, tolerance_percentage=500):
        '''
        Validates that user inputed hours/mileage is not too low or too high.
        tolerance_percentage greater value == more leeway.
        '''

        hours_or_mileage = asset_obj.hours_or_mileage.lower()

        history_exists = AssetModelHistory.objects.using(db_name).filter(VIN=asset_obj.VIN).exists()

        # Mileage or Both
        if hours_or_mileage == AssetModel.Mileage.lower() or hours_or_mileage == AssetModel.Both.lower():
            mileage_delta = mileage - asset_obj.mileage
            if mileage < asset_obj.mileage:
                extra_info = "Expected new mileage to be atleast " + str(asset_obj.mileage) + " but got " + str(mileage)
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.AUMF_0, extra_info))
                return Response(CustomError.get_full_error_json(CustomError.AUMF_0, extra_info), status=status.HTTP_400_BAD_REQUEST)
            if history_exists:
                expected_mileage = AssetHelper.get_expected_mileage_since_last_usage_update(asset_obj)
                if not HelperMethods.a_within_x_percent_greater_than_b(mileage_delta, expected_mileage, tolerance_percentage):
                    extra_info = "Expected delta of no more than " + str(expected_mileage + expected_mileage * (tolerance_percentage / 100)) + " mileage but got " + str(mileage_delta)
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.AUMF_1, extra_info))
                    return Response(CustomError.get_full_error_json(CustomError.AUMF_1, extra_info), status=status.HTTP_400_BAD_REQUEST)

        # Hours or Both
        if hours_or_mileage == AssetModel.Hours.lower() or hours_or_mileage == AssetModel.Both.lower():
            hours_delta = hours - asset_obj.hours
            if hours < asset_obj.hours:
                extra_info = "Expected new hours to be atleast " + str(asset_obj.hours) + " but got " + str(hours)
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.AUHF_0, extra_info))
                return Response(CustomError.get_full_error_json(CustomError.AUHF_0, extra_info), status=status.HTTP_400_BAD_REQUEST)
            if history_exists:
                expected_hours = AssetHelper.get_expected_hours_since_last_usage_update(asset_obj)
                if not HelperMethods.a_within_x_percent_greater_than_b(hours_delta, expected_hours, tolerance_percentage):
                    extra_info = "Expected delta of no more than " + str(expected_hours + expected_hours * (tolerance_percentage / 100)) + " hours but got " + str(hours_delta)
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.AUHF_1, extra_info))
                    return Response(CustomError.get_full_error_json(CustomError.AUHF_1, extra_info), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def usage_parameters_provided(asset_obj, data):
        '''
        Checks if request.data includes the usage fields that are relevant to the asset.
        '''
        valid_usage = True
        hours_or_mileage = str(asset_obj.hours_or_mileage).lower()
        if hours_or_mileage == AssetModel.Mileage:
            if (len(str(data.get("mileage"))) == 0 or data.get("mileage") is None):
                valid_usage = False
        elif hours_or_mileage == AssetModel.Hours:
            if (len(str(data.get("hours"))) == 0 or data.get("hours") is None):
                valid_usage = False
        elif hours_or_mileage == AssetModel.Both:
            if ((len(str(data.get("mileage"))) == 0 or data.get("mileage") is None) or
            (len(str(data.get("hours"))) == 0 or data.get("hours") is None)):
                valid_usage = False

        return valid_usage

    @staticmethod
    def get_expected_mileage_since_last_usage_update(asset_obj):
        latest_mileage = AssetModelHistory.objects.filter(VIN=asset_obj.VIN).values('mileage').distinct().latest('date').get('mileage')
        latest_mileage_date = AssetModelHistory.objects.filter(VIN=asset_obj.VIN, mileage=latest_mileage).values('date').earliest('date').get('date')
        days_since = HelperMethods.get_datetime_delta(latest_mileage_date, datetime.utcnow(), delta_format="days")
        if days_since < 1:
            days_since = 1
        expected_mileage = asset_obj.daily_average_mileage * days_since
        if asset_obj.daily_average_mileage < 20:
            expected_mileage = 20 * days_since
        #print("Days since last mileage: " + str(days_since))
        #print("Expected mileage: " + str(expected_mileage))
        return expected_mileage

    @staticmethod
    def get_expected_hours_since_last_usage_update(asset_obj):
        latest_hours = AssetModelHistory.objects.filter(VIN=asset_obj.VIN).values('hours').distinct().latest('date').get('hours')
        latest_hours_date = AssetModelHistory.objects.filter(VIN=asset_obj.VIN, hours=latest_hours).values('date').earliest('date').get('date')
        days_since = HelperMethods.get_datetime_delta(latest_hours_date, datetime.utcnow(), delta_format="days")
        if days_since < 1:
            days_since = 1
        expected_hours = asset_obj.daily_average_hours * days_since
        if asset_obj.daily_average_hours < 3:
            expected_hours = 3 * days_since
        #print("Days since last hours: " + str(days_since))
        #print("Expected hours: " + str(expected_hours))
        return expected_hours

    @staticmethod
    def validate_asset_status(status):
        if status in dict(AssetModel.status_choices):
            return True
        return False

    @staticmethod
    def validate_hours_or_mileage(status):
        if status in dict(AssetModel.hours_or_mileage_choices):
            return True
        return False

    @staticmethod
    def validate_purpose(purpose):
        if purpose in dict(AssetFile.file_purpose_choices):
            return True
        return False

    @staticmethod
    def asset_circular_dependency_check(VIN, parent_VIN, db_name):
        return AssetModel.objects.using(db_name).get(VIN=VIN) in AssetModel.objects.get(VIN=parent_VIN).get_parents()
        
    @staticmethod
    def asset_exists(VIN, db_name):
        return AssetModel.objects.using(db_name).filter(VIN=VIN).exists()

    @staticmethod
    def asset_is_active(VIN, db_name):
        return AssetModel.objects.using(db_name).filter(VIN=VIN, status=AssetModel.Active).exists()

    @staticmethod
    def asset_is_inop(VIN, db_name):
        return AssetModel.objects.using(db_name).filter(VIN=VIN, status=AssetModel.Inop).exists()

    @staticmethod
    def assets_exist(VIN_list, db_name):
        for VIN in VIN_list:
            if not AssetHelper.asset_exists(VIN, db_name):
                return False
        return True

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_all_assets(db_name):
        return AssetModel.objects.using(db_name).all()

    @staticmethod
    def get_all_assets_at_company(db_name):
        return AssetModel.objects.using(db_name).exclude(status=AssetModel.Disposed)

    @staticmethod
    def get_asset_by_VIN(VIN, db_name):
        return AssetModel.objects.using(db_name).get(VIN=VIN)

    @staticmethod
    def get_assets_from_VIN_list(vin_list, db_name):
        return AssetModel.objects.using(db_name).filter(VIN__in=vin_list)

    @staticmethod
    def get_assets_not_in_VIN_list_and_active(vin_list, db_name):
        return AssetModel.objects.using(db_name).filter(status=AssetModel.Active).exclude(VIN__in=vin_list)

    @staticmethod
    def get_asset_location_id(VIN, db_name):
        return AssetModel.objects.using(db_name).values_list('current_location', flat=True).get(VIN=VIN)

    @staticmethod
    def get_asset_managers(VIN, db_name):
        location_id = AssetHelper.get_asset_location_id(VIN, db_name)
        return DetailedUser.objects.using(db_name).filter(location__in=[location_id], role_permissions=2)

    @staticmethod
    def get_asset_managers_emails(VIN, db_name):
        location_id = AssetHelper.get_asset_location_id(VIN, db_name)
        return DetailedUser.objects.using(db_name).filter(location__in=[location_id], role_permissions=2).values_list('email', flat=True)

    @staticmethod
    def get_asset(pk):
        try:
            return AssetModel.objects.get(pk=pk)
        except AssetModel.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

    @staticmethod
    def get_assets_by_VIN_contains(substring, db_name):
        return AssetModel.objects.using(db_name).filter(VIN__icontains=substring)

    @staticmethod    
    def get_assets_by_VIN_endswith(substring, db_name):
        return AssetModel.objects.using(db_name).filter(VIN__iendswith=substring)

    @staticmethod
    def get_asset_by_unit_number(unit_number, db_name):
        try:
            return AssetModel.objects.using(db_name).get(unit_number=unit_number)
        except AssetModel.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

    @staticmethod
    def get_asset_by_unit_number_contains(substring, db_name):
        return AssetModel.objects.using(db_name).filter(unit_number__icontains=substring)

    @staticmethod    
    def get_assets_by_unit_number_endswith(substring, db_name):
        return AssetModel.objects.using(db_name).filter(unit_number__iendswith=substring)

    @staticmethod
    def get_all_asset_files(db_name):
        return AssetFile.objects.using(db_name).all()

    @staticmethod
    def get_asset_files_by_vin(vin, db_name):
        return AssetFile.objects.using(db_name).filter(VIN=vin)

    @staticmethod
    def check_asset_status_active(vin, db_name, allow_inoperative=True):
        config_obj = AssetHelper.get_asset_by_VIN(vin, db_name)
        if config_obj.status == AssetModel.Disposed:
            return False
        else:
            if allow_inoperative is False and config_obj.status == AssetModel.Inop:
                return False
        return True
    
    ######################### Get all annual reports by vin
    @staticmethod
    def get_annual_report_by_vin(vin, db_name):
        try:
            asset_obj = AssetFile.objects.using(db_name).filter(file_purpose='annual_report', VIN=vin)
            #returning multiple files for annual_report
            for asset in asset_obj:
                secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, asset.file_purpose, asset.file_url)
                asset.file_url = secure_file_url
            return asset_obj
        except AssetFile.DoesNotExist:
            return []

    #########################

    @staticmethod
    def get_ins_files_by_vin(vin, db_name, detailed_user):
        try:
            asset_obj = AssetFile.objects.using(db_name).filter(file_purpose='insurance', VIN=vin).latest('date_created')
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, asset_obj.file_purpose, asset_obj.file_url)
            asset_obj.file_url = secure_file_url
            return [asset_obj]
        except AssetFile.DoesNotExist:
            return []

    @staticmethod
    def get_reg_files_by_vin(vin, db_name, detailed_user):
        try:
            asset_obj = AssetFile.objects.using(db_name).filter(file_purpose='registration', VIN=vin).latest('date_created')
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, asset_obj.file_purpose, asset_obj.file_url)
            asset_obj.file_url = secure_file_url
            return [asset_obj]
        except AssetFile.DoesNotExist:
            return []
    
    @staticmethod
    def get_warranty_files_by_vin(vin, db_name, detailed_user):
        try:
            asset_obj = AssetFile.objects.using(db_name).filter(file_purpose='warranty', VIN=vin)
            #returning multiple files for warranty
            for asset in asset_obj:
                secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, asset.file_purpose, asset.file_url)
                asset.file_url = secure_file_url
            return asset_obj
        except AssetFile.DoesNotExist:
            return []

    @staticmethod
    def get_all_reg_files_by_vin(vin, db_name, detailed_user):
        try:
            asset_obj = AssetFile.objects.using(db_name).filter(file_purpose='registration', VIN=vin)
            #returning multiple files for registration
            for asset in asset_obj:
                secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, asset.file_purpose, asset.file_url)
                asset.file_url = secure_file_url
            return asset_obj
        except AssetFile.DoesNotExist:
            return []
    
    @staticmethod
    def get_all_ins_files_by_vin(vin, db_name, detailed_user):
        try:
            asset_obj = AssetFile.objects.using(db_name).filter(file_purpose='insurance', VIN=vin)
            #returning multiple files for insurance
            for asset in asset_obj:
                secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, asset.file_purpose, asset.file_url)
                asset.file_url = secure_file_url
            return asset_obj
        except AssetFile.DoesNotExist:
            return []
    # .order_by('-pk')[:3][::-1] - in case we decide to return 3 latest as initially discussed

    @staticmethod
    def get_all_vins_for_user(user):
        return AssetHelper.filter_assets_for_maintenance_for_user(AssetModel.objects.using(user.db_access).all().exclude(status=AssetModel.Disposed), user).values_list('VIN', flat=True)

    @staticmethod
    def get_all_vins(db_name):
        return AssetModel.objects.using(db_name).all().exclude(status=AssetModel.Disposed).values_list('VIN', flat=True)

    @staticmethod
    def get_all_tracked_assets(db_name):
        return AssetModel.objects.using(db_name).all().exclude(hours_or_mileage=AssetModel.Neither, status=AssetModel.Disposed)

    @staticmethod
    def get_previous_different_status(asset_obj, db_name):
        try:
            previous_asset_entry = AssetModelHistory.objects.using(db_name).filter(VIN__VIN = asset_obj.VIN).exclude(status=asset_obj.status).order_by('-date').first()
            if previous_asset_entry.status == "NA" or previous_asset_entry.status == "" or previous_asset_entry.status == None:
                return asset_obj.status
            return previous_asset_entry.status
        except Exception as e: 
            return asset_obj.status

    @staticmethod
    def get_previous_different_last_process(asset_obj, db_name):
        try:
            previous_asset_entry = AssetModelHistory.objects.using(db_name).filter(VIN__VIN = asset_obj.VIN).exclude(last_process=asset_obj.last_process).order_by('-date').first()
            if previous_asset_entry.last_process == "NA" or previous_asset_entry.last_process == "" or previous_asset_entry.last_process is None:
                return asset_obj.last_process
            return previous_asset_entry.last_process
        except Exception as e: 
            return asset_obj.last_process

    @staticmethod
    def get_asset_file_entries_for_daterange(start_date, end_date, db_name):
        return AssetFile.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_assets_for_daterange(start_date, end_date, db_name):
        return AssetModel.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_asset_history_for_daterange(start_date, end_date, db_name):
        return AssetModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_assets_by_parent(parent_VIN, db_name):
        return AssetModel.objects.using(db_name).filter(parent=parent_VIN)

    # ----------------------------------------------------------------------------------------------

    # Get all historic records for asset within the daterange from sample days before today to today. Find out what subset of time we have records for from that initial range. 
    @staticmethod
    def calculate_average_daily_usage(VIN, hours_or_mileage, sample_days, db_name, latest_mileage=-1, latest_hours=-1):
        try:
            if hours_or_mileage == AssetModel.Neither.lower():
                return 0, 0

            sample_end_date = HelperMethods.naive_to_aware_utc_datetime(datetime.utcnow())
            sample_start_date = HelperMethods.naive_to_aware_utc_datetime(HelperMethods.subtract_time_from_datetime(sample_end_date, sample_days, time_unit="days"))

            # print("start_date: " + str(sample_start_date))
            # print("end_date: " + str(sample_end_date))

            hours_list = [0]
            mileage_list = [0]
            history_available_range = [0]

            asset_history_qs = AssetModelHistory.objects.using(db_name).filter(VIN=VIN, date__range=[sample_start_date, sample_end_date]).order_by('date')
            history_available_range = list(asset_history_qs.values_list('date', flat=True))

            if history_available_range:
                actual_days = HelperMethods.get_datetime_delta(history_available_range[0], sample_end_date, delta_format="days")
                if actual_days == 0:
                    actual_days = 1
                # print("Actual days: " + str(actual_days))

                if hours_or_mileage == AssetModel.Hours:
                    hours_list = list(asset_history_qs.values_list('hours', flat=True))
                    
                elif hours_or_mileage == AssetModel.Mileage:
                    mileage_list = list(asset_history_qs.values_list('mileage', flat=True))
                
                elif hours_or_mileage == AssetModel.Both:
                    hours_list = list(asset_history_qs.values_list('hours', flat=True))
                    mileage_list = list(asset_history_qs.values_list('mileage', flat=True))

                # If latest hours/mileage not passed in, we go with latest in history
                if latest_mileage == -1 or not latest_mileage:
                    latest_mileage = mileage_list[-1]
                if latest_hours == -1 or not latest_hours:
                    latest_hours = hours_list[-1]

                # Latest usage figure - oldest usage figure
                total_mileage = latest_mileage - mileage_list[0]
                # print("total_mileage: " + str(total_mileage))
                average_daily_mileage = total_mileage / actual_days
                # print("average_daily_mileage: " + str(average_daily_mileage))

                total_hours = latest_hours - hours_list[0]
                # print("total_hours: " + str(total_hours))
                average_daily_hours = total_hours / actual_days
                # print("average_daily_hours: " + str(average_daily_hours))

                return average_daily_mileage, average_daily_hours

            else:
                # print("No records found in sample daterange...")
                return 0, 0

        except ZeroDivisionError as zde:
            Logger.getLogger().error(zde)
            return 0, 0

    # ----------------------------------------------------------------------------------------------

    def get_asset_files_from_blob(files_qs, db_name):
        # Create FileInfo list from the asset file qs
        file_infos = []
        for file in files_qs:
            file_infos.append(FileInfo(file_type=file.get('file_type'), bytes=file.get('bytes'), file_name=file.get('file_name'),
            blob_container='asset', file_url=file.get('file_url')))

        # Get list of FileInfo objects that hold the file bytes in the file variable
        file_infos = BlobStorageHelper.get_files_from_blob(db_name, blob_container_name='asset', file_infos=file_infos)

        # Convert to SimpleUploadFile
        simple_files = []
        for file_info in file_infos:
            simple_files.append(SimpleUploadedFile(file_info.file_name, file_info.file, file_info.file_type))

        simple_files.sort(key=lambda f: f.size, reverse=True)

        return simple_files

    # ----------------------------------------------------------------------------------------------

    # Will return similar assets in two lists. One ordered by mileage and the other by hours
    @staticmethod
    def get_similar_assets(vin, database):
        asset = AssetModel.objects.using(database).get(VIN=vin)
        if asset.equipment_type is not None:
            sim_assets_by_mileage = AssetModel.objects.using(database).filter(equipment_type=asset.equipment_type,hours_or_mileage=AssetModel.Mileage).exclude(VIN=vin)
            sim_assets_by_hours = AssetModel.objects.using(database).filter(equipment_type=asset.equipment_type,hours_or_mileage=AssetModel.Hours).exclude(VIN=vin)
            sim_assets_by_both = AssetModel.objects.using(database).filter(equipment_type=asset.equipment_type,hours_or_mileage=AssetModel.Both).exclude(VIN=vin)
            sim_assets_by_neither = AssetModel.objects.using(database).filter(equipment_type=asset.equipment_type,hours_or_mileage=AssetModel.Neither).exclude(VIN=vin)

            if sim_assets_by_mileage.count() >= sim_assets_by_hours.count():
                sim_assets_by_mileage = sim_assets_by_mileage | sim_assets_by_both | sim_assets_by_neither
            else:
                sim_assets_by_hours = sim_assets_by_hours | sim_assets_by_both | sim_assets_by_neither

            sim_assets_by_mileage = sim_assets_by_mileage.order_by('daily_average_mileage')
            sim_assets_by_hours = sim_assets_by_hours.order_by('daily_average_hours')

            # Convert QuerySets to list of AssetModel instances
            sim_assets_by_mileage = list(sim_assets_by_mileage)
            sim_assets_by_hours = list(sim_assets_by_hours)

            return sim_assets_by_mileage, sim_assets_by_hours
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.AUET_0))
            return None, None

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_similar_assets_make_model(vin, database):
        asset = AssetModel.objects.using(database).get(VIN=vin)

        # Retrieve assets with the same equipment type ID (meaning they have the same make and model) as the asset with the given VIN
        similar_assets = AssetModel.objects.using(database).filter(equipment_type=asset.equipment_type).exclude(VIN=vin)

        # Order the similar assets by daily average mileage
        similar_assets = similar_assets.order_by('daily_average_mileage')

        # Convert QuerySet to a list of AssetModel instances
        similar_assets = list(similar_assets)

        return similar_assets
        

    @staticmethod
    def filter_asset_query(item_list):
        '''
        Get the first/latest record from a value list.

        '''
        context_dict = {}
        for i in item_list:
            seen_assets = []
            unique_records = []
            for item in item_list[i]:
                if item['VIN'] not in seen_assets:
                    unique_records.append(item)
                    seen_assets.append(item["VIN"])
            context_dict[i] = unique_records
        return context_dict

    # ----------------------------------------------------------------------------------------------
    
    # secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, asset.file_purpose, asset.file_url)
    # asset.file_url = secure_file_url
    @staticmethod
    def secure_asset_file_ser_urls(ser_data, db_name):
        '''
        Adds security token to blob urls in serialized list of file jsons.
        '''
        updated_ser_data = []
        for file_json in ser_data:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name,
            'asset/' + BlobStorageHelper.clean_container_name(file_json['file_purpose']), file_json['file_url'])
            file_json['file_url'] = str(secure_file_url)
            updated_ser_data.append(file_json)
        return updated_ser_data

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_allowed_file_types_for_purpose(purpose):
        # ["application/pdf", "text/plain", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetFile.asset_image:
            return ["image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetFile.vin_support:
            return ["image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetFile.usage_support:
            return ["image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetFile.warranty:
            return ["application/pdf", "text/plain"]
        if purpose == AssetFile.insurance:
            return ["application/pdf", "text/plain"]
        if purpose == AssetFile.registration:
            return ["application/pdf", "text/plain"]
        if purpose == AssetFile.invoice:
            return ["application/pdf", "text/plain"]
        if purpose == AssetFile.other_support:
            return ["application/pdf", "text/plain", "image/jpeg", "image/png", "image/heic", "image/heif"]
        if purpose == AssetFile.other:
            return ["application/pdf", "text/plain"]
        return []

    # ----------------------------------------------------------------------------------------------

    @staticmethod
    def get_all_engines(db_name):
        return EngineModel.objects.using(db_name).all()

    @staticmethod
    def get_engines_with_asset(db_name,asset):
        return AssetHelper.get_all_engines(db_name).filter(VIN=asset.VIN)

    @staticmethod
    def get_all_asset_expiration_dates(db_name, VIN_list):
        return AssetHelper.get_all_asset_files(db_name).filter(VIN__in=VIN_list, file_purpose=AssetFile.registration)

    @staticmethod
    def filter_asset_expiration_date(asset_files):
        """
            Filter the latest expiration date of each asset.
        """
        latest_exp = {}
        for file in asset_files:
            latest = latest_exp.get(file.VIN)
            if latest:
                if latest >= file.expiration_date:
                    continue
            latest_exp[file.VIN_id] = file.expiration_date

        return latest_exp if latest_exp else None