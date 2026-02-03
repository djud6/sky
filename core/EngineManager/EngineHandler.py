import logging
import traceback

from rest_framework import status
from rest_framework.response import Response

from GSE_Backend.errors.ErrorDictionary import CustomError
from api.Models.engine import EngineModel
from api.Serializers.serializers import EngineSerializer, EngineHistorySerializer
from .EngineHelper import EngineHelper
from ..AssetManager.AssetHelper import AssetHelper


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class EngineHandler:

    @staticmethod
    def handle_add(user, data, dry_run=False):
        try:
            vin = data.get("VIN")
            if not vin:
                return Response(CustomError.I_0, status.HTTP_400_BAD_REQUEST)

            vessel = AssetHelper.get_asset_by_VIN(vin, user.db_access)

            name = data.get("name")
            if not name:
                return Response(CustomError.I_0, status.HTTP_400_BAD_REQUEST)

            hours = data.get("hours")
            hours = float(hours) if hours else 0

            engine = EngineModel(
                VIN=vessel,
                name=name,
                hours=hours
            )

            if dry_run:
                return Response(status=status.HTTP_200_OK)
            else:
                engine.save(using=user.db_access)

                EngineHelper.log_create(user, engine)

                serializer = EngineSerializer(engine)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_remove(user, data):
        try:
            engine_id = data.get("engine_id")
            if not engine_id:
                return Response(CustomError.I_0, status.HTTP_400_BAD_REQUEST)

            engine, response = EngineHelper.get_by_id(user.db_access, engine_id)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            EngineHelper.log_delete(user, engine)

            engine.delete()

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update(user, data, dry_run=False, responsible_request=None, create_if_necessary=False,
                      vin_for_creation=None):
        try:
            creating = False
            db_name = user.db_access

            engine_id = data.get("engine_id")
            if not engine_id:
                if create_if_necessary:
                    creating = True
                else:
                    return Response(CustomError.I_0, status.HTTP_400_BAD_REQUEST)

            if creating:
                data["VIN"] = vin_for_creation
                return EngineHandler.handle_add(user, data, dry_run)
            else:
                engine, response = EngineHelper.get_by_id(db_name, engine_id)
                if response.status_code != status.HTTP_302_FOUND:
                    return response

            anything_changed = False

            new_name = data.get("name")
            if new_name and new_name != engine.name:
                engine.name = new_name
                anything_changed = True

            new_hours = float(data.get("hours"))
            if new_hours and new_hours != engine.hours:
                engine.hours = new_hours

                # Every time the hours is updated, the daily_average_hours for this engine should be updated too.
                daily_average_hours = EngineHelper.calculate_average_daily_usage(engine.engine_id,
                                                                                 90,
                                                                                 db_name,
                                                                                 new_hours)
                engine.daily_average_hours = daily_average_hours
                anything_changed = True

            if anything_changed and not dry_run:
                response = EngineHelper.log_update(user, engine, responsible_request)
                if response.status_code != status.HTTP_202_ACCEPTED:
                    return response
                engine.save()

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_multiple(user, engines, responsible_request=None, create_if_necessary=False,
                               vin_for_creation=None):
        try:
            for dry_run in [True, False]:
                for engine in engines:
                    response = EngineHandler.handle_update(user, engine, dry_run, responsible_request,
                                                           create_if_necessary, vin_for_creation)
                    if response.status_code != status.HTTP_200_OK:
                        return response
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_bulk_update_multiple(user, asset_list, request_by_vin=None):

        for asset in asset_list:
            engines = asset.get('engines')
            responsible_request = request_by_vin.get(asset.get("VIN"))
            if responsible_request is None:
                continue

            if engines:
                response = EngineHandler.handle_update_multiple(user, engines, responsible_request)
                if response.status_code != status.HTTP_200_OK:
                    return response
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def handle_get_history(user, id):
        try:
            engine, response = EngineHelper.get_by_id(user.db_access, id)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            histories, response = EngineHelper.get_history_for_engine(user.db_access, engine)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            serializer = EngineHistorySerializer(histories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get(user, id):
        try:
            engine, response = EngineHelper.get_by_id(user.db_access, id)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            serializer = EngineSerializer(engine)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_by_vin(user, vin):
        try:
            engines, response = EngineHelper.get_all_by_vin(user.db_access, vin)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            serializer = EngineSerializer(engines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_history_by_vin(user, vin):
        try:
            histories, response = EngineHelper.get_history_by_vin(user.db_access, vin)
            if response.status_code != status.HTTP_302_FOUND:
                return response

            serializer = EngineHistorySerializer(histories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0, e),
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_is_usage_valid(request_data, user):
        try:
            db_name = user.db_access
            engine_obj, response = EngineHelper.get_by_id(db_name, request_data.get('engine_id'))
            if response.status_code != status.HTTP_302_FOUND:
                return response
            hours = request_data.get('hours')
            return EngineHelper.validate_usage_update(engine_obj, hours, db_name, tolerance_percentage=300)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
