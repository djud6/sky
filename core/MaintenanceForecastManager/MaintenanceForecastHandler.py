import logging

from rest_framework import status
from rest_framework.response import Response

from GSE_Backend.errors.ErrorDictionary import CustomError
from api.Serializers.serializers import (MaintenanceForecastRulesSerializer,
                                         LightAssetModelSerializer,
                                         LightMaintenanceForecastRulesSerializer)
from ..AssetManager.AssetHelper import AssetHelper
from ..Helper import HelperMethods
from ..HistoryManager.MaintenanceHistory import MaintenanceHistory
from ..InspectionTypeManager.InspectionTypeHelper import InspectionTypeHelper
from ..MaintenanceForecastManager.MaintenanceForecastHelper import MaintenanceForecastHelper
from ..MaintenanceForecastManager.MaintenanceForecastUpdater import MaintenanceForecastUpdater
from ..MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from ..MaintenanceManager.MaintenanceUpdater import MaintenanceUpdater


class Logger:
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceForecastHandler:

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_maintenance_forecast_rule(request_data, user):
        try:
            data = MaintenanceHelper.update_maintenance_dict(request_data.get("data", None), user.db_access)
            apply_to_all = request_data.get("apply_to_similar_type", None)
            apply_to_all = HelperMethods.validate_bool(str(apply_to_all))
            if (data != None and apply_to_all != None):
                ser = MaintenanceForecastRulesSerializer(data=data)
                if (ser.is_valid()):
                    # check asset forcast rule
                    check_response = MaintenanceHelper.check_maintenance_cycle_inputs(data, user.db_access)
                    if check_response.status_code != status.HTTP_200_OK:
                        return check_response

                    # validate the cycle inputs
                    validation_response = MaintenanceHelper.validate_maintenance_cycle_inputs(data)
                    if validation_response.status_code != status.HTTP_200_OK:
                        return validation_response

                    # Check to see if similar rule already exists in the database
                    if (MaintenanceForecastHelper.validate_entry(ser)):
                        maint_forecast_obj = ser.save()

                        # update fields after db entry has been made
                        maint_forecast_obj, created_by_status = MaintenanceUpdater.update_maintenance_rule_post_creation(
                            maint_forecast_obj, user)
                        if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                            return created_by_status

                        # create asset event log
                        description = "Maintenance rule " + str(
                            maint_forecast_obj.custom_id) + " was added for this asset."
                        event_log_response = MaintenanceHistory.create_maintenance_rule_event_log(maint_forecast_obj,
                                                                                                  description)
                        if event_log_response.status_code != status.HTTP_201_CREATED:
                            return event_log_response

                        # create maintenance forecast record
                        if (not MaintenanceHistory.create_maintenance_forecast_record(maint_forecast_obj)):
                            Logger.getLogger().error(CustomError.MHF_2)
                            return Response(CustomError.get_full_error_json(CustomError.MHF_2),
                                            status=status.HTTP_400_BAD_REQUEST)

                    else:
                        maint_forecast_obj, update_response = MaintenanceForecastUpdater.update_full_maintenance_rule(
                            ser.validated_data, user.db_access)
                        if update_response.status_code != status.HTTP_202_ACCEPTED:
                            return update_response

                        # set modified_by
                        maint_forecast_obj, modified_by_status = MaintenanceUpdater.update_maintenance_rule_modified_by(
                            maint_forecast_obj, user)
                        if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                            return modified_by_status

                        # create asset event log
                        description = "Maintenance rule " + str(maint_forecast_obj.custom_id) + " was updated."
                        event_log_response = MaintenanceHistory.create_maintenance_rule_event_log(maint_forecast_obj,
                                                                                                  description)
                        if event_log_response.status_code != status.HTTP_201_CREATED:
                            return event_log_response

                        # create maintenance forecast record
                        if (not MaintenanceHistory.create_maintenance_forecast_record(maint_forecast_obj)):
                            Logger.getLogger().error(CustomError.MHF_2)
                            return Response(CustomError.get_full_error_json(CustomError.MHF_2),
                                            status=status.HTTP_400_BAD_REQUEST)

                        return Response(ser.data, status=status.HTTP_200_OK)

                    # Code to handle if apply to all is selected

                    if apply_to_all:
                        # get similar assets by make and model
                        similar_assets = AssetHelper.get_similar_assets_make_model(data.get('VIN'), user.db_access)
                        for asset in similar_assets:
                            # Prepare asset-specific data dictionary
                            asset_specific_data = data.copy()
                            asset_specific_data['VIN'] = asset.VIN

                            # Create a new Serializer instance for each asset
                            ser_asset_specific = MaintenanceForecastRulesSerializer(data=asset_specific_data)

                            if ser_asset_specific.is_valid():
                                check_response = MaintenanceHelper.check_maintenance_cycle_inputs(asset_specific_data,
                                                                                                  user.db_access)
                                if check_response.status_code != status.HTTP_200_OK:
                                    return check_response

                                validation_response = MaintenanceHelper.validate_maintenance_cycle_inputs(
                                    asset_specific_data)
                                if validation_response.status_code != status.HTTP_200_OK:
                                    return validation_response

                                if MaintenanceForecastHelper.validate_entry(ser_asset_specific):
                                    maint_forecast_obj = ser_asset_specific.save()
                                    maint_forecast_obj, created_by_status = MaintenanceUpdater.update_maintenance_rule_post_creation(
                                        maint_forecast_obj, user)
                                    if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                                        return created_by_status

                                    description = f"Maintenance rule {maint_forecast_obj.custom_id} was added for this asset."
                                    event_log_response = MaintenanceHistory.create_maintenance_rule_event_log(
                                        maint_forecast_obj, description)
                                    if event_log_response.status_code != status.HTTP_201_CREATED:
                                        return event_log_response

                                    if not MaintenanceHistory.create_maintenance_forecast_record(maint_forecast_obj):
                                        Logger.getLogger().error(CustomError.MHF_2)
                                        return Response(CustomError.get_full_error_json(CustomError.MHF_2),
                                                        status=status.HTTP_400_BAD_REQUEST)
                            else:
                                Logger.getLogger().error(
                                    CustomError.get_error_dev(CustomError.S_0, ser_asset_specific.errors))
                                return Response(
                                    CustomError.get_full_error_json(CustomError.S_0, ser_asset_specific.errors),
                                    status=status.HTTP_400_BAD_REQUEST)

                        # TODO Code for applying to similar asset type goes here
                    return Response(status=status.HTTP_201_CREATED)

                else:
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                    return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(CustomError.get_full_error_json(CustomError.I_0), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_maintenance_forecast_rules(user):
        try:
            qs = MaintenanceForecastHelper.get_maintenance_forecast_rules(user.db_access)
            relevant_qs = MaintenanceHelper.select_related_to_maintenance_rule(
                MaintenanceHelper.filter_maintenance_rules_for_user(qs, user))
            ser = LightMaintenanceForecastRulesSerializer(relevant_qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_maintenance_forecast_rules_by_vin(_vin, user):
        try:
            qs = MaintenanceForecastHelper.get_maintenance_forecast_rules_by_vin(_vin, user.db_access)
            relevant_qs = MaintenanceHelper.select_related_to_maintenance_rule(
                MaintenanceHelper.filter_maintenance_rules_for_user(qs, user))
            ser = LightMaintenanceForecastRulesSerializer(relevant_qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_maintenance_forecast_rule_details_by_id(maintenance_rule_id, user):
        try:
            maintenance_rule, maintenance_response = MaintenanceForecastHelper.get_maintenance_forecast_rule_by_id(
                maintenance_rule_id, user.db_access)
            if maintenance_response.status_code != status.HTTP_302_FOUND:
                return maintenance_response
            ser = LightMaintenanceForecastRulesSerializer(maintenance_rule)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_maintenance_forecast_rule_details_by_custom_id(custom_maintenance_rule_id, user):
        try:
            (maintenance_rule,
             maintenance_response) = MaintenanceForecastHelper.get_maintenance_forecast_rule_by_custom_id(
                custom_maintenance_rule_id, user.db_access)
            if maintenance_response.status_code != status.HTTP_302_FOUND:
                return maintenance_response

            ser = LightMaintenanceForecastRulesSerializer(maintenance_rule)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_maintenance_forecast_for_rule(request_data, user):
        try:
            inspection_type_id = request_data.get("inspection_type_id")
            date_range_start = request_data.get("start_date")
            date_range_end = request_data.get("end_date")
            db_name = user.db_access

            inspection_type_obj, inspection_type_response = InspectionTypeHelper.get_inspection_type_by_id(
                inspection_type_id, db_name)
            if inspection_type_response.status_code != status.HTTP_302_FOUND:
                return inspection_type_response

            if not HelperMethods.is_valid_date_range(date_range_start, date_range_end):
                Logger.getLogger().error(CustomError.IDR_0)
                return Response(CustomError.get_full_error_json(CustomError.IDR_0), status=status.HTTP_400_BAD_REQUEST)

            date_range_start = HelperMethods.date_string_to_datetime(date_range_start).replace(tzinfo=None)
            date_range_end = HelperMethods.date_string_to_datetime(date_range_end).replace(tzinfo=None)

            (assets_VIN_list,
             assets_maintenance_date,
             assets_potential_maintenance_VIN_list,
             forecast_response) = MaintenanceForecastHelper.forecast_maintenance(db_name,
                                                                                 inspection_type_obj,
                                                                                 date_range_start,
                                                                                 date_range_end)
            if forecast_response.status_code != status.HTTP_200_OK:
                return forecast_response

            all_assets = AssetHelper.get_all_assets(user.db_access)
            context = AssetHelper.get_serializer_context_2(all_assets, user)

            in_range_assets_qs = AssetHelper.get_assets_from_VIN_list(assets_VIN_list, db_name)
            in_range_assets_qs = AssetHelper.select_related_to_asset(in_range_assets_qs)
            in_range_ser = LightAssetModelSerializer(in_range_assets_qs, many=True, context=context)

            potential_assets_qs = AssetHelper.get_assets_from_VIN_list(assets_potential_maintenance_VIN_list, db_name)
            potential_assets_qs = AssetHelper.select_related_to_asset(potential_assets_qs)
            potential_ser = LightAssetModelSerializer(potential_assets_qs, many=True, context=context)

            return Response({"in_range_assets": MaintenanceForecastHelper.add_forecast_date_to_maintenance_ser(
                in_range_ser.data, assets_maintenance_date),
                "potential_assets": potential_ser.data},
                status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
