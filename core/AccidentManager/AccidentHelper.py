from core.HistoryManager.AccidentHistory import AccidentHistory
from rest_framework.response import Response
from rest_framework import status
from api.Models.accident_report import AccidentModel
from api.Models.accident_file import AccidentFileModel
from api.Models.accident_report_history import AccidentModelHistory
from api.Models.DetailedUser import DetailedUser
from api.Models.RolePermissions import RolePermissions
from ..UserManager.UserHelper import UserHelper
from ..IssueManager.IssueHelper import IssueHelper
from ..RepairManager.RepairHelper import RepairHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from ..Helper import HelperMethods
from datetime import datetime, timedelta
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.utils import timezone
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AccidentHelper():

    @staticmethod
    def select_related_to_accident(queryset):
        return queryset.select_related('created_by', 'modified_by', 'location', "VIN__current_location", "VIN__original_location", 'VIN__department', 'VIN__equipment_type__asset_type')

    @staticmethod
    def get_accident_ser_context(accident_id_list, db_name):
        # Get accident files and secure urls
        container_name = "accidents"
        accident_files = AccidentFileModel.objects.using(db_name).filter(accident__in=accident_id_list).order_by('-file_id').values()
        for accident_file in accident_files:
            secure_file_url = BlobStorageHelper.get_secure_blob_url(db_name, container_name, accident_file.get('file_url'))
            accident_file['file_url'] = secure_file_url
        return {
            'accident_files': accident_files
            }

    # This method will take a accidents qs and filter it to only show accidents relevant to user
    @staticmethod
    def filter_accidents_for_user(accident_qs, user):
        detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
        
        if(detailed_user.role_permissions.role == RolePermissions.executive):
            return accident_qs

        user_locations = UserHelper.get_user_locations_by_user_obj(detailed_user)
        return accident_qs.filter(location__in=user_locations)

    # -------------------------------------------------------------------------------------

    @staticmethod
    def get_all_accidents(db_name):
        return AccidentModel.objects.using(db_name).select_related('location').all()

    @staticmethod
    def get_all_ids_with_disposals(db_name):
        return set(AccidentModel.objects.using(db_name).exclude(disposal__isnull=True).values_list('disposal', flat=True))

    @staticmethod
    def get_accidents_by_vin(_vin, db_name):
        return AccidentModel.objects.using(db_name).filter(VIN__VIN=_vin)

    @staticmethod
    def get_accident_by_id(accident_id, db_name):
        try:
            return AccidentModel.objects.using(db_name).get(accident_id=accident_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADNE_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ADNE_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_accident_by_custom_id(accident_custom_id, db_name):
        try:
            return AccidentModel.objects.using(db_name).get(custom_id=accident_custom_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADNE_1, e))
            return None, Response(CustomError.get_full_error_json(CustomError.ADNE_1, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_accident_exists(accident_id, db_name):
        return AccidentModel.objects.using(db_name).filter(accident_id=accident_id).exists()

    @staticmethod
    def get_accident_by_vin_and_is_operational(vin, is_operational, db_name):
        return AccidentModel.objects.using(db_name).filter(VIN=vin, is_operational=is_operational)

    @staticmethod
    def get_accidents_after_date_by_resolved_status_and_location(resolved_status, date, location_id, db_name):
        return AccidentModel.objects.using(db_name).filter(date_created__gte=date, is_resolved=resolved_status, location=location_id)

    @staticmethod
    def get_accidents_after_date(date, db_name):
        return AccidentModel.objects.using(db_name).filter(date_created__gte=date)

    @staticmethod
    def get_accidents_for_daterange(start_date, end_date, db_name):
        return AccidentModel.objects.using(db_name).filter(date_created__range=[start_date, end_date])

    @staticmethod
    def get_accident_history_for_daterange(start_date, end_date, db_name):
        return AccidentModelHistory.objects.using(db_name).filter(date__range=[start_date, end_date])

    @staticmethod
    def get_accident_file_entries_for_daterange(start_date, end_date, db_name):
        return AccidentFileModel.objects.using(db_name).filter(file_created__range=[start_date, end_date])

    @staticmethod
    def get_accident_location(accident_obj):
        if accident_obj.location != None:
            return accident_obj.location
        else: # If None return 0 as there are no location IDs that are 0
            return 0

    # -------------------------------------------------------------------------------------

    @staticmethod
    def is_accident_preventable(accident_id, db_name):
        return AccidentModel.objects.using(db_name).values_list('is_preventable', flat=True).get(accident_id=accident_id)

    @staticmethod
    def is_accident_operational(accident_id, db_name):
        return AccidentModel.objects.using(db_name).values_list('is_operational', flat=True).get(accident_id=accident_id)


    # Calculate downtime for accidents that are unresolved and caused the asset to be non-operational
    @staticmethod
    def unresolved_inop_accident_downtime(accident_qs):
        dt_hours = 0
        for accident in accident_qs:
            now = datetime.utcnow()
            accident_date_created = accident.date_created
            dt_hours += HelperMethods.get_datetime_delta(start=accident_date_created, end=now, delta_format="hours")
        return dt_hours

    # Calculate downtime for accidents that are unresolved but where the asset was still active after the accident
    @staticmethod
    def unresolved_active_accident_downtime(accident_qs):
        dt_hours = 0
        for accident in accident_qs:
            now = datetime.utcnow()
            accident_date_created = accident.date_created
            dt_hours += HelperMethods.get_datetime_delta(start=accident_date_created, end=now, delta_format="hours")
        return dt_hours


    @staticmethod
    def get_downtime_for_accidents(accidents, db_name):
        all_accidents = list(accidents.values_list('accident_id', 'is_operational', 'date_created', 'date_returned_to_service', 'is_preventable'))
        all_issues = list(IssueHelper.get_all_issues(db_name).values_list('accident_id__accident_id', 'repair_id__available_pickup_date'))
        utcnow = datetime.utcnow()

        preventable_downtime = 0
        non_preventable_downtime = 0

        for accident in all_accidents:
            accident_id = accident[0]
            accident_is_operational = accident[1]
            accident_date_created = accident[2]
            accident_date_returned_to_service = accident[3]
            accident_is_preventable = accident[4]

            # At first we assume asset was inop after accident, so we set downtime start
            # as the date accident was created. We also set downtime end to now, but if
            # asset has been returned to service we set it to that date instead.
            downtime_start = accident_date_created
            downtime_end = utcnow
            if accident_date_returned_to_service is not None:
                downtime_end = accident_date_returned_to_service

            # If asset was operational after accident, downtime does not start 
            # till earliest pickup date for the repair that fixes issues caused by accident.
            if accident_is_operational:
                earliest_pickup_date = utcnow 
                for issue in all_issues:
                    issue_accident_id = issue[0]
                    issue_pickup_date = issue[1]
                    if issue_accident_id == accident_id:
                        if issue_pickup_date is not None:
                            if HelperMethods.datetime_a_later_than_datetime_b(earliest_pickup_date, issue_pickup_date):
                                earliest_pickup_date = issue_pickup_date

                # If we have found a pickup date then make it the start of the downtime
                # else it means that there have been no repairs related to this accident
                # thus the accident has so far caused no downtime. Skip to next accident.
                if earliest_pickup_date != utcnow:
                    downtime_start = earliest_pickup_date
                else:
                    continue

            accident_downtime =  HelperMethods.get_datetime_delta(start=downtime_start, end=downtime_end, delta_format="hours")
            if accident_downtime < 0:
                accident_downtime = 0

            if accident_is_preventable:
                preventable_downtime += accident_downtime
            else:
                non_preventable_downtime += accident_downtime

        return preventable_downtime, non_preventable_downtime

    # -------------------------------------------------------------------------------------

    @staticmethod
    def get_downtime_for_accidents_list(accidents, db_name):
        all_accidents = accidents.values_list('accident_id', 'is_operational', 'date_created', 'date_returned_to_service', 'is_preventable')
        all_issues = IssueHelper.get_all_issues(db_name).values_list('accident_id__accident_id', 'repair_id__available_pickup_date')
        utcnow = timezone.now()

        preventable_downtime = timedelta()
        non_preventable_downtime = timedelta()

        for accident in all_accidents:
            accident_id, accident_is_operational, accident_date_created, accident_date_returned_to_service, accident_is_preventable = accident

            downtime_start = accident_date_created
            downtime_end = utcnow

            if accident_date_returned_to_service is not None:
                downtime_end = accident_date_returned_to_service

            if accident_is_operational:
                earliest_pickup_date = utcnow

                for issue in all_issues:
                    issue_accident_id, issue_pickup_date = issue

                    if issue_accident_id == accident_id and issue_pickup_date is not None:
                        if HelperMethods.datetime_a_later_than_datetime_b(earliest_pickup_date, issue_pickup_date):
                            earliest_pickup_date = issue_pickup_date

                if earliest_pickup_date != utcnow:
                    downtime_start = earliest_pickup_date
                else:
                    continue

            accident_downtime = downtime_end - downtime_start

            if accident_downtime < timedelta():
                accident_downtime = timedelta()

            if accident_is_preventable:
                preventable_downtime += accident_downtime
            else:
                non_preventable_downtime += accident_downtime

        return preventable_downtime, non_preventable_downtime
    
    
    @staticmethod
    def update_accident_dict(request_data, db_name):
        request_data["location"] = AssetHelper.get_asset_location_id(request_data.get("VIN"), db_name)
        return request_data
    
    # -------------------------------------------------------------------------------------
    
    @staticmethod
    def get_accidents_by_vin_date_range(vin, start_date, end_date, db_access):
        # Assuming accidents are stored in a database table called "Accident"
        accidents = AccidentModel.objects.filter(VIN=vin, date_created__range=(start_date, end_date))

        preventable_count = 0
        non_preventable_count = 0

        for accident in accidents:
            if accident.is_preventable:
                preventable_count += 1
            else:
                non_preventable_count += 1

        return preventable_count, non_preventable_count
