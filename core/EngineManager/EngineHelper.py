import logging
import traceback
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response

from GSE_Backend.errors.ErrorDictionary import CustomError
from api.Models.engine import EngineModel, EngineHistoryAction, EngineHistoryModel
from ..Helper import HelperMethods
from ..UserManager.UserHelper import UserHelper


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class EngineHelper:

    @staticmethod
    def get_all(db_name):
        return EngineModel.objects.using(db_name).all()

    @staticmethod
    def get_by_name(db_name, target_name):
        try:
            return EngineModel.objects.using(db_name).get(name=target_name), Response(status=status.HTTP_302_FOUND)
        except:
            return None, Response(CustomError.get_full_error_json(CustomError.G_0), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_by_id(db_name, target_id):
        try:
            return EngineModel.objects.using(db_name).get(engine_id=target_id), Response(status=status.HTTP_302_FOUND)
        except:
            return None, Response(CustomError.get_full_error_json(CustomError.G_0), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_all_by_vin(db_name, vin):
        try:
            return EngineModel.objects.using(db_name).filter(VIN=vin), Response(status=status.HTTP_302_FOUND)
        except:
            return None, Response(CustomError.get_full_error_json(CustomError.G_0), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def log_common(user, engine, action, responsible_request=None):
        try:
            history = EngineHistoryModel(
                action=action,
                responsible_user=UserHelper.get_detailed_user_obj(user.email, user.db_access),
                engine_id=engine,
                updated_name=engine.name,
                updated_hours=engine.hours,
            )

            responsible_type = None
            if responsible_request:
                try:
                    responsible_type = responsible_request.work_order.split("-")[1]
                except AttributeError:
                    # Because Daily Operational Check model has a different name for work_order field, we need to
                    # validate if it has to use custom_id or worke_order
                    responsible_type = responsible_request.custom_id.split("-")[1]

            if responsible_type == "m":
                # Maintenance Request is responsible for the update
                history.responsible_maintenance_id = responsible_request.pk
            elif responsible_type == "r":
                # Repair Request is responsible for the update
                history.responsible_repair_id = responsible_request.pk
            elif responsible_type == 'dc':
                # Daily Operational Check is responsible for the update
                history.responsible_daily_check_id = responsible_request.pk

            history.save(using=user.db_access)
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def log_create(user, engine):
        return EngineHelper.log_common(user, engine, EngineHistoryAction.Create)

    @staticmethod
    def log_update(user, engine, responsible_request=None):
        return EngineHelper.log_common(user, engine, EngineHistoryAction.Update, responsible_request)

    @staticmethod
    def log_delete(user, engine):
        return EngineHelper.log_common(user, engine, EngineHistoryAction.Delete)

    @staticmethod
    def get_history_for_engine(db_name, engine):
        try:
            return EngineHistoryModel.objects.using(db_name).filter(engine_id=engine), Response(
                status=status.HTTP_302_FOUND)
        except:
            traceback.print_exc()
            return None, Response(CustomError.get_full_error_json(CustomError.G_0), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_history_by_vin(db_name, vin):
        engines, response = EngineHelper.get_all_by_vin(db_name, vin)
        if response.status_code != status.HTTP_302_FOUND:
            return None, response

        histories = []
        for engine in engines:
            engineHistories, response = EngineHelper.get_history_for_engine(db_name, engine)
            if response.status_code != status.HTTP_302_FOUND:
                return None, response
            histories += engineHistories

        return histories, Response(status=status.HTTP_302_FOUND)

    @staticmethod
    def calculate_average_daily_usage(engine_id, sample_days, db_name, latest_hours=-1):
        """
            Get all historic records for engine within the daterange from sample days before today to today.
            Find out what subset of time we have records for from that initial range.
        """
        try:
            sample_end_date = HelperMethods.naive_to_aware_utc_datetime(datetime.utcnow())
            sample_start_date = HelperMethods.naive_to_aware_utc_datetime(
                HelperMethods.subtract_time_from_datetime(sample_end_date, sample_days, time_unit="days"))

            engine_history_qs = (EngineHistoryModel.objects.using(db_name)
                                 .filter(engine_id_id=engine_id,
                                         date__range=[sample_start_date,
                                                      sample_end_date])
                                 .order_by('date'))

            history_available_range = list(engine_history_qs.values_list('date', flat=True))

            if history_available_range:
                actual_days = HelperMethods.get_datetime_delta(history_available_range[0], sample_end_date,
                                                               delta_format="days")
                if actual_days == 0:
                    actual_days = 1

                hours_list = list(engine_history_qs.values_list('updated_hours', flat=True))

                # If latest hours not passed in, we go with latest in history
                if latest_hours == -1 or not latest_hours:
                    latest_hours = hours_list[-1]

                # Latest usage figure - oldest usage figure
                total_hours = latest_hours - hours_list[0]
                daily_average_hours = total_hours / actual_days

                return daily_average_hours

            else:
                # No history available
                return 0

        except ZeroDivisionError as zde:
            Logger.getLogger().error(zde)
            return 0

    @staticmethod
    def get_expected_hours_since_last_usage_update(engine_obj, db_name):
        latest_hours = (EngineHistoryModel.objects.using(db_name).filter(engine_id_id=engine_obj.engine_id)
                        .values('updated_hours')
                        .distinct()
                        .latest('date')
                        .get('updated_hours'))

        latest_hours_date = (EngineHistoryModel.objects.using(db_name).filter(engine_id_id=engine_obj.engine_id,
                                                                              updated_hours=latest_hours)
                             .values('date')
                             .earliest('date')
                             .get('date'))

        days_since = HelperMethods.get_datetime_delta(latest_hours_date, datetime.utcnow(), delta_format="days")
        if days_since < 1:
            days_since = 1
        expected_hours = engine_obj.daily_average_hours * days_since
        if engine_obj.daily_average_hours < 3:
            expected_hours = 3 * days_since
        return expected_hours

    @staticmethod
    def validate_usage_update(engine_obj, hours, db_name, tolerance_percentage):
        """
        Validates that user inputted hours is not too low or too high.
        tolerance_percentage greater value == more leeway.
        """

        history_exists = engine_obj.enginehistorymodel_set.exists()
        hours_delta = hours - engine_obj.hours
        if hours < engine_obj.hours:
            extra_info = f"Expected new hour to be at least {engine_obj.hours} but got {hours}."
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.EUHF_0, extra_info))
            return Response(CustomError.get_full_error_json(CustomError.EUHF_0, extra_info),
                            status=status.HTTP_400_BAD_REQUEST)

        if history_exists:
            expected_hours = EngineHelper.get_expected_hours_since_last_usage_update(engine_obj, db_name)
            if not HelperMethods.a_within_x_percent_greater_than_b(hours_delta, expected_hours, tolerance_percentage):
                expected_hours_with_tolerance = expected_hours + expected_hours * (tolerance_percentage / 100)
                extra_info = (f"Expected delta of no more than {expected_hours_with_tolerance} hours "
                              f"but got {hours_delta}.")
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.EUHF_1, extra_info))
                return Response(CustomError.get_full_error_json(CustomError.EUHF_1, extra_info),
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
